"""periodical_requests_recorder -"""

import datetime
import json
import logging
import sys
import traceback
from pathlib import Path

import cloudscraper
import crython
import pandas as pd
import yagmail
import yaml
from pyquery import PyQuery

__version__ = "0.2.4"
__author__ = "fx-kirin <fx.kirin@gmail.com>"
__all__ = ["RequestsRecorder"]


USE_HEALTH_CHECK = False
try:
    import kanihealth

    USE_HEALTH_CHECK = True
except ImportError:
    pass


class RequestsRecorder:
    def __init__(self, headers=None):
        self.log = logging.getLogger(self.__class__.__name__)
        if headers is None:
            self.headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101"
                    " Firefox/82.0"
                ),
                "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
                "Connection": "keep-alive",
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                ),
                "Accept-Encoding": "gzip, deflate, br",
                "Cache-Control": "max-age=0",
            }
        else:
            self.headers = headers
        self.session = cloudscraper.create_scraper()
        self.gmail_address = None
        self.gmail_password = None
        self.mail_to = None
        self.yag = None

    def load_yaml(self, yaml_path):
        now = datetime.datetime.now()
        if isinstance(yaml_path, str):
            yaml_path = Path(yaml_path)

        assert isinstance(yaml_path, Path)

        cron_data = yaml.safe_load(yaml_path.read_text())
        if "gmail_address" in cron_data:
            self.gmail_address = cron_data["gmail_address"]
            if "mail_to" in cron_data:
                self.mail_to = cron_data["mail_to"]
            if "gmail_password" in cron_data:
                self.gmail_password = cron_data["gmail_password"]
            elif "gmail_oauth" in cron_data:
                self.yag = yagmail.SMTP(
                    self.gmail_address, oauth2_file=cron_data["gmail_oauth"]
                )
            else:
                raise AssertionError
            cron_data = cron_data["tasks"]

        for cron in cron_data:
            assert isinstance(cron, dict)
            for key in ["name", "url", "record_dir", "output_file_format", "cron_expr"]:
                assert key in cron
            cron["record_dir"] = Path(cron["record_dir"]).expanduser().absolute()

            def recorder(cron):
                self.record(cron)

            recorder.__name__ = cron["name"]
            crython.job(expr=cron["cron_expr"], cron=cron)(recorder)
            self.log.info(f"cron registered {cron=}")
            if "get_data_on_start" in cron and cron["get_data_on_start"]:
                self.log.info("Record on starting.")
                self.record(cron)

    def record(self, cron):
        self.log.info(f"Recording {cron=}")
        if "url_format" in cron:
            iteration = cron["iteration"]
        else:
            use_pandas = False
            if "pandas_csv" in cron:
                use_pandas = cron["pandas_csv"]

            try:
                result = self.session.get(cron["url"])
                if result.status_code == 200:
                    now = datetime.datetime.now()
                    output_file = cron["output_file_format"].format(**cron)
                    output_file = now.strftime(output_file)
                    output_file = cron["record_dir"] / Path(output_file)
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    if "target_elements" in cron:
                        elem = PyQuery(result.text)
                        if isinstance(cron["target_elements"], dict):
                            target = cron["target_elements"]
                            if "index" not in target:
                                target["index"] = 0
                            elem = elem(target["element"])[target["index"]]
                            if use_pandas:
                                df = pd.read_html(elem.html)[0]
                                df.to_csv(output_file)
                            else:
                                output_file.write_text(elem.text_content())
                            if USE_HEALTH_CHECK:
                                kanihealth.update_health(cron["name"])
                        elif isinstance(cron["target_elements"], list):
                            output = {}
                            for target in cron["target_elements"]:
                                if "name" not in target:
                                    raise AssertionError("target must has name")
                                if "index" not in target:
                                    target["index"] = 0
                                elem = elem.find(target["element"])[target["index"]]
                                output[target["name"]] = elem.text_content()
                            output_file.write_text(json.dumps(output))
                            if USE_HEALTH_CHECK:
                                kanihealth.update_health(cron["name"])
                        else:
                            raise AssertionError
                    else:
                        if "encoding" in cron:
                            output_file.write_text(
                                result.content.decode(cron["encoding"])
                            )
                            if USE_HEALTH_CHECK:
                                kanihealth.update_health(cron["name"])
                        else:
                            output_file.write_bytes(result.content)
                            if USE_HEALTH_CHECK:
                                kanihealth.update_health(cron["name"])
                else:
                    error_msg = (
                        f"Requests failed {cron=} status_code:{result.status_code}"
                    )
                    self.log.error(error_msg)
                    if self.yag is not None:
                        self.yag.send(
                            to=self.mail_to,
                            subject="periocial_recorder failed.",
                            contents=error_msg,
                        )
                        self.log.info("Sent error mail.")
            except Exception:
                self.log.error(sys.exc_info())
                self.log.error(traceback.format_exc())
                error_msg = f"cron:\n{cron}\nsys.exc_info:\n{sys.exc_info()}\ntraceback:\n{traceback.format_exc()}"
                if self.yag is not None:
                    self.yag.send(
                        to=self.mail_to,
                        subject="periocial_recorder failed.",
                        contents=error_msg,
                    )
                    self.log.info("Sent error mail.")

    def start(self):
        crython.start()
        crython.join()
