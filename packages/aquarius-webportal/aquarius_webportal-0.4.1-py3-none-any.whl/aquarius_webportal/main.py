import io
import urllib.parse

import requests
from lxml import html
import pandas as pd


class AquariusWebPortal:
    """Access data from a deployment of Aquarius Web Portal.

    Args:
        server (str): URL of the Web Portal deployment.
        session (optional): requests.Session object to use

    The main methods to use are:

    - :meth:`aquarius_webportal.AquariusWebPortal.fetch_locations`: fetch metadata for all locations
    - :meth:`aquarius_webportal.AquariusWebPortal.fetch_datasets`: fetch metadata for datasets measuring a queried parameter
    - :meth:`aquarius_webportal.AquariusWebPortal.fetch_dataset`: fetch data for a single timeseries

    Relevant attributes of the ``AquariusWebPortal`` object are:

    Attributes:
        server (str): as initialised
        params (pd.DataFrame): the available parameters. If the
            portal is disclaimer-blocked, this will be empty (see
            ReadTheDocs documentation for further details)
        session: reqeusts.Session object

    """

    def __init__(self, server="water.data.sa.gov.au", session=None, **kwargs):
        if not server.startswith("http"):
            server = "https://" + server
        if session:
            self.session = session
        else:
            self.session = requests.Session(**kwargs)
        self.server = server
        self.params = self.fetch_params()

    def fetch_params(self, payload=None):
        """Fetch the list of available parameters.

        Returns:
            pd.DataFrame: a table of available parameters with these
            columns:

                - param_id (int)
                - param_name (str)
                - param_desc (str)

        """
        r1 = self.session.post(self.server + "/Data/List/", payload)
        return parse_params_from_html(r1.text)

    def get_param(self, param_name=None, param_desc=None, param_id=None):
        """Fetch/identify a single parameter from the ``params`` attribute.

        Args:
            param_name (str): select a parameter with this name
            param_desc (str): select a parameter with the description (note
                that usually the description functions as a "long name")
            param_id (int): select the parameter with this ID number

        Returns:
            pd.Series: the relevant row from ``self.params`` with these
            fields:

                - param_id (int)
                - param_name (str)
                - param_desc (str)

        """
        if param_name:
            return self.params[self.params.param_name == param_name].iloc[0]
        elif param_desc:
            return self.params[self.params.param_desc == param_desc].iloc[0]
        elif param_id:
            return self.params[self.params.param_id == param_id].iloc[0]

    def fetch_locations(self):
        """Fetch a list of all locations from the portal.

        Returns:
            pd.DataFrame: a table of location metadata. The available fields
            may vary between different portals, but these may be present:

                - wp_loc_id (called "LocationId" in the AQWP internal APIs)
                - lon (called "LocX" in the AQWP internal APIs)
                - lat (called "LocY" in the AQWP internal APIs)
                - loc_name (called "Location" in the AQWP internal APIs)
                - loc_id (called "LocationIdentifier" in the AQWP internal APIs)
                - loc_type (called "LocType" in the AQWP internal APIs)
                - loc_folder (called "LocationFolder" in the AQWP internal APIs)

        """
        return self.fetch_list()

    def fetch_datasets(self, param_name=None, param_desc=None, param_id=None):
        """Fetch a list of all datasets from the portal with a given parameter

        Args:
            param_name (str): select a parameter with this name
            param_desc (str): select a parameter with the description (note
                that usually the description functions as a "long name")
            param_id (int): select the parameter with this ID number

        Returns:
            pd.DataFrame: a table of dataset metadata. The available fields
            may vary between different portals, but these may be present:

                - wp_loc_id (called "LocationId" in the AQWP internal APIs)
                - wp_dset_id (called "DatasetId" in the AQWP internal APIs)
                - lon (called "LocX" in the AQWP internal APIs)
                - lat (called "LocY" in the AQWP internal APIs)
                - loc_name (called "Location" in the AQWP internal APIs)
                - loc_id (called "LocationIdentifier" in the AQWP internal APIs)
                - dset_name (called "DatasetIdentifier" in the AQWP internal APIs)
                - loc_type (called "LocType" in the AQWP internal APIs)
                - loc_folder (called "LocationFolder" in the AQWP internal APIs)
                - dset_start (called "StartOfRecord" in the AQWP internal APIs)
                - dset_end (called "EndOfRecord" in the AQWP internal APIs)
                - param (str) - derived from dset_name
                - label (str) - derived from dset_name

        """
        if not param_id:
            params = self.fetch_params()
            if param_name in params.param_name.unique():
                param_id = params[params.param_name == param_name].param_id.iloc[0]
            if param_desc in params.param_desc.unique():
                param_id = params[params.param_desc == param_desc].param_id.iloc[0]
        if param_id is None:
            return Exception("failed to identify parameter")
        else:
            return self.fetch_list(param_id=param_id)

    def fetch_list(self, param_id=None):
        """Internal function that fetches list data from the /Data/Data_List
        endpoint.

        Args:
            param_id (int): if not supplied, the list is of Locations.
                If supplied, the list is of Datasets/Time series.

        Returns:
            pd.DataFrame: a table of results with some columns renamed for
            convenience:

                - wp_loc_id (called "LocationId" in the AQWP internal APIs)
                - wp_dset_id (called "DatasetId" in the AQWP internal APIs)
                - lon (called "LocX" in the AQWP internal APIs)
                - lat (called "LocY" in the AQWP internal APIs)
                - loc_name (called "Location" in the AQWP internal APIs)
                - loc_id (called "LocationIdentifier" in the AQWP internal APIs)
                - dset_name (called "DatasetIdentifier" in the AQWP internal APIs)
                - loc_type (called "LocType" in the AQWP internal APIs)
                - loc_folder (called "LocationFolder" in the AQWP internal APIs)
                - dset_start (called "StartOfRecord" in the AQWP internal APIs)
                - dset_end (called "EndOfRecord" in the AQWP internal APIs)
                - classification (called "Classification" in the AQWP internal APIs)
                - bgcolor (called "Background" in the AQWP internal APIs)
                - seq (called "Sequence" in the AQWP internal APIs)
                - param (str) - derived from dset_name if the latter exists
                - label (str) - derived from dset_name if the latter exists

            Any other columns will not be renamed.

        """
        page_size = 5000
        page_no = 1
        request_complete = False
        results = []
        total_results = None
        n = 0
        while (request_complete) is False and n < 15:
            query = {
                "page": page_no,
                "pageSize": page_size,
            }
            if param_id is not None:
                query["parameters[0]"] = param_id
            url = self.server + "/Data/Data_List?" + urllib.parse.urlencode(query)
            resp = self.session.post(url, data=query)
            data = resp.json()

            if n == 0:
                total_results = data["Total"]

            results += data["Data"]
            n += 1

            if len(results) < total_results:
                page_no += 1
            else:
                request_complete = True

        df = pd.DataFrame(results)
        df = df.rename(
            columns={
                "LocationId": "wp_loc_id",
                "DatasetId": "wp_dset_id",
                "LocX": "lon",
                "LocY": "lat",
                "Location": "loc_name",
                "LocationIdentifier": "loc_id",
                "DatasetIdentifier": "dset_name",
                "LocType": "loc_type",
                "LocationFolder": "loc_folder",
                "StartOfRecord": "dset_start",
                "EndOfRecord": "dset_end",
                "Classification": "classification",
                "Background": "bgcolor",
                "Sequence": "seq",
            }
        )
        if "dset_name" in df:
            df["param"] = df.dset_name.apply(lambda v: v.split("@")[0].split(".")[0])
            df["label"] = df.dset_name.apply(lambda v: v.split("@")[0].split(".")[1])
        return df

    def fetch_dataset(
        self,
        dset_name,
        date_range=None,
        extra_data_types=None,
        start=None,
        finish=None,
        session=None,
        **kwargs,
    ):
        """Fetch timeseries data for a single dataset.

        Args:
            dset_name (str): the dataset name as ``param.label@location`` - you can
                get this from the dset_name column of the table returned by
                :meth:`aquarius_webportal.AquariusWebPortal.fetch_datasets`
            extra_data_types (str/sequence): The additional metadata fields
                to retrieve for each data point - either "all", None, or
                a sequence of strings with one or more of "grade", "approval", "qualifier",
                and "interpolation_type". None is the default.
            data_range (str): either None (the default) or "Days7"
            start (pd.Timestamp): earliest data to retrieve - None by default
            finish (pd.Timestamp): latest data to retrieve - None by default

        There are three ways of querying to speed things up, and these are
        selected depending on the values of the **date_range**, **start** and
        **finish** arguments:

        (1) Entire period of record - the default - leave the **date_range**,
        **start** and **finish** arguments null.

        (2) A custom period - leave **date_range** null and
        provide **start** and **finish** arguments.

        (3) The last week - use "Days7" for **date_range** and leave
        **start** and **finish** null.

        Returns:
            pd.DataFrame: a table of timeseries data. The table has a
            DateTimeIndex with timezone-aware timestamps. The time zone
            is derived from that provided by Aquarius Web portal in the header
            of the CSV which is downloaded in the background by this function.
            The first column will be the requested parameter (short) name
            with its unit in parentheses e.g. "Discharge (m^3/s)". Following
            columns will be the extra_data_types if requested.

        """
        query = {
            "Calendar": "CALENDARYEAR",
            "Interval": "PointsAsRecorded",
            "Step": 1,
            "ExportFormat": "csv",
            "TimeAligned": True,
            "RoundData": True,
            "Datasets[0].DatasetName": dset_name,
        }

        if date_range is None and start is None and finish is None:
            query["DateRange"] = "EntirePeriodOfRecord"
        elif start and finish:
            query["DateRange"] = "Custom"
            query["StartTime"] = pd.Timestamp(start).strftime("%Y-%m-%d %H:%M")
            query["EndTime"] = pd.Timestamp(finish).strftime("%Y-%m-%d %H:%M")
        elif date_range == "Days7":
            query["DateRange"] = "Days7"

        if extra_data_types == "all":
            extra_data_types = ["grade", "approval", "qualifier", "interpolation_type"]
        elif not extra_data_types:
            extra_data_types = []

        query["IncludeGradeCodes"] = (True if "grade" in extra_data_types else False,)
        query["IncludeApprovalLevels"] = (
            True if "approval" in extra_data_types else False,
        )
        query["IncludeQualifiers"] = (
            True if "qualifier" in extra_data_types else False,
        )
        query["IncludeInterpolationTypes"] = (
            True if "interpolation_type" in extra_data_types else False,
        )

        url = self.server + "/Export/BulkExport"

        skiprows = 0
        resp = self.session.get(url, data=query)
        header = resp.text[:500].splitlines()
        for i, line in enumerate(header):
            if line.startswith("Timestamp ("):
                skiprows = i
        header_line = header[skiprows - 1].split(",")
        if skiprows == 0:
            print(f"Error:\n{header}")

        with io.StringIO(resp.text) as f:
            df = pd.read_csv(
                f,
                skiprows=4,
            )
            cols = [
                df.columns[0],
                df.columns[1].replace("Value", header_line[1].split(".")[0]),
            ] + header_line[2:]
        df.columns = cols

        index_col = cols[0]
        tz_offset = index_col.split("(UTC")[1][:-1].replace(":", "")
        df[index_col] = df[index_col] + " " + tz_offset
        df[index_col] = pd.to_datetime(df[cols[0]], format="%Y-%m-%d %H:%M:%S %z")
        df = df.set_index(index_col)
        return df


def parse_params_from_html(source):
    """Obtain a list of parameter names, descriptions, and IDs
    from the HTML source of a Web Portal page (either the List
    or Map pages will work).

    Returns:
        pd.DataFrame: a table of available parameters with these
        columns:

            - param_id (int)
            - param_name (str)
            - param_desc (str)

    """
    root = html.document_fromstring(source)
    params = []
    for element in root.xpath("//option[@data-code]"):
        attrs = element.attrib
        params.append(
            {
                "param_id": attrs["value"],
                "param_name": attrs["data-code"],
                "param_desc": element.text,
            }
        )
    pdf = pd.DataFrame(params, columns=["param_id", "param_name", "param_desc"])
    pdf = pdf[
        ~pd.isnull(pdf.param_id.apply(lambda v: pd.to_numeric(v, errors="coerce")))
    ]
    return pdf.drop_duplicates()
