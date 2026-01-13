"""
This converter converts from EnviDat to JsonLD, based on the Zenodo version.

Opposed to the envidat to datacite converter, this is pretty small and clean, so i kept it as one file.

"""
import csv
import json
from io import StringIO
from typing import Any
from datetime import datetime
import xml.etree.ElementTree as ET

import requests
from shapely.geometry import shape
from requests import get

from envidat_converters.logic.converter_logic.encoding_helper import encoding_format_helper


class EnviDatToJsonLD:
    # TAGS JSON LD
    context_tag = "@context"
    type_tag = "@type"
    id_tag = "@id"
    identifier_tag = "identifier"
    url_tag = "url"
    inLanguage_tag = "inLanguage"
    contentSize_tag = "contentSize"
    size_tag = "size"
    publisher_tag = "publisher"
    name_tag = "name"
    alternateName_tag = "alternateName"
    datePublished_tag = "datePublished"
    creator_tag = "creator"
    author_tag = "author"
    givenName_tag = "givenName"
    familyName_tag = "familyName"
    affiliation_tag = "affiliation"
    keywords_tag = "keywords"
    temporal_tag = "temporal"
    temporal_coverage_tag = "temporalCoverage"
    sameAs_tag = "sameAs"
    distribution_tag = "distribution"
    content_url_tag = "contentUrl"
    encoding_format_tag = "encodingFormat"
    spatial_tag = "spatialCoverage"
    license_tag = "license"
    citation_tag = "citation"

    units = {
        "kb": 1024,
        "mb": 1024**2,
        "gb": 1024**3,
        "tb": 1024**4,
    }

    license_spdx = {
        "odc-odbl": "https://spdx.org/licenses/ODbL-1.0",
        "cc-by": "https://spdx.org/licenses/CC-BY-4.0",
        "cc-by-sa": "https://spdx.org/licenses/CC-BY-SA-4.0",
        "cc-by-nc": "https://spdx.org/licenses/CC-BY-NC-4.0",
        "CC0-1.0": "https://spdx.org/licenses/CC0-1.0",
    }
    wsl_data_license_url = "https://www.envidat.ch/#/policies"

    doi_url = "https://doi.org/"

    dictionary = {
        "name": "title",
        "description": "notes",
        # Note on the dates: Zenodo uses these for TECHNICAL metadata
        "dateCreated": "metadata_created",
        "dateModified": "metadata_modified",
        "version": "version",
    }

    def __init__(self, dataset: dict):
        self.jld = {
            self.context_tag: "http://schema.org",
            self.type_tag: "https://schema.org/Dataset",
            self.url_tag: f"https://envidat.ch/#/metadata/{dataset['name']}",
            self.id_tag: f"{self.doi_url}{dataset["doi"]}",
            self.identifier_tag: f"{self.doi_url}{dataset["doi"]}",
            self.sameAs_tag: {
                self.type_tag: "Dataset",
                self.id_tag: f"https://envidat.ch/#/metadata/{dataset['id']}",
            },
            # Note: we currently only have english entries and only plan to use english.
            self.inLanguage_tag: {
                self.alternateName_tag: "eng",
                self.type_tag: "Language",
                self.name_tag: "English",
            },
            self.publisher_tag: {
                self.id_tag: "https://www.envidat.ch",
                self.url_tag: "https://www.envidat.ch",
                self.sameAs_tag: "https://www.re3data.org/repository/r3d100012587",
                self.type_tag: "Organization",
                self.name_tag: json.loads(dataset.get("publication")).get("publisher"),
            },
            self.contentSize_tag: self._handle_sizes(dataset.get("resources")),
            self.size_tag: self._handle_sizes(dataset.get("resources")),
            self.datePublished_tag: json.loads(dataset.get("publication")).get(
                "publication_year"
            ),
            self.creator_tag: self._handle_creators(dataset.get("author")),
            self.author_tag: self._handle_creators(dataset.get("author")),
            self.keywords_tag: self._handle_keywords(dataset.get("tags")),
            self.temporal_tag: self._handle_temporal(dataset.get("date")),
            self.temporal_coverage_tag: self._handle_temporal_coverage(dataset.get("date")),
            self.distribution_tag: self._handle_distribution(
                dataset.get("resources"), dataset.get("doi")
            ),
            self.citation_tag: self._handle_citation(
                dataset.get("doi"), dataset.get("related_publications")
            )
        }

        if spatial_coverage := self._handle_spatial(dataset.get("spatial")):
            self.jld[self.spatial_tag] = spatial_coverage

        if lic := self._handle_license(
                dataset.get("doi"),
                dataset.get("license_id"),
                dataset.get("license_url")
        ):
            self.jld[self.license_tag] = lic

        # Note that zenodo does not seem to convert spatial information to json-ld (at this point)

        for key, value in self.dictionary.items():
            entry = dataset.get(value, "")
            if entry:
                self.jld[key] = entry

    def to_json_str(self):
        return json.dumps(self.jld, indent=4)

    def get(self):
        return self.jld

    def _handle_sizes(self, resources):
        total_size = 0

        for resource in resources:
            size = self._size_helper(
                resource.get("size", ""), resource.get("resource_size", "")
            )
            if size:
                total_size += int(size)

        if total_size > self.units["tb"]:
            result = f"{round(total_size / self.units['tb'])} TB"
        elif total_size > self.units["gb"]:
            result = f"{round(total_size / self.units['gb'], 2)} GB"
        elif total_size > self.units["mb"]:
            result = f"{round(total_size / self.units['mb'], 2)} MB"
        elif total_size > self.units["kb"]:
            result = f"{round(total_size / self.units['kb'], 2)} KB"
        else:
            result = f"{total_size} bytes"
        return result

    def _handle_creators(self, authors):
        authors = json.loads(authors)
        creators = []
        for author in authors:
            affiliations = []
            affiliations_list = []
            affiliation_field_names = [
                "affiliation",
                "affiliation_02",
                "affiliation_03",
            ]
            for affiliation_field in affiliation_field_names:
                if author.get(affiliation_field):
                    affiliations_list.append(author.get(affiliation_field))

            for affiliation in affiliations_list:
                affiliations.append(
                    {self.type_tag: "Organization", self.name_tag: affiliation}
                )

            creator = {
                self.type_tag: "Person",
                self.name_tag: f"{author.get('name')}, {author.get('given_name')}",
                self.givenName_tag: author.get("given_name"),
                self.familyName_tag: author.get("name"),
                self.affiliation_tag: affiliations,
            }

            id = author.get("identifier", "")
            if id:
                creator[self.id_tag] = id
            creators.append(creator)
        return creators

    def _handle_keywords(self, keywords):
        keyword_list = [keyword["display_name"] for keyword in keywords]
        return ", ".join(keyword_list)

    def _handle_temporal(self, dates):
        temporal = []
        # in zenodo i only found temporal used for all dates without any info on what is what
        # also, have not found a date range example
        dates = json.loads(dates)
        for date in dates:
            start_date = date.get("date")
            end_date = date.get("end_date", False)

            if start_date and end_date:
                temporal.append(f"{start_date} - {end_date}")
            else:
                temporal.append(f"{start_date}")

        return temporal

    def _handle_temporal_coverage(self, dates) -> str:
        """
        Convert EnviDat 'dates' list into JSON-LD 'temporalCoverage' string.
        """
        temporal_coverage = ""
        dates_list = json.loads(dates)

        # Use collected dates first
        collected = [d for d in dates_list if d.get("date_type") == "collected"]
        created = [d for d in dates_list if d.get("date_type") == "created"]
        selected = collected if collected else created

        # Collect valid date objects
        start_dates = []
        end_dates = []

        for dte in selected:
            start_str = dte.get("date")
            end_str = dte.get("end_date")

            try:
                if start_str:
                    start_dates.append(datetime.fromisoformat(start_str))
                if end_str:
                    end_dates.append(datetime.fromisoformat(end_str))
            except ValueError:
                print(f"Invalid date format in entry: {dte}")
                continue

        if not start_dates:
            return temporal_coverage

        min_date = min(start_dates)
        max_date = max(end_dates) if end_dates else None

        # If only one record or no valid end_date, return single date
        if not max_date or max_date <= min_date:
            temporal_coverage = min_date.date().isoformat()
        else:
            temporal_coverage = f"{min_date.date().isoformat()}/{max_date.date().isoformat()}"

        return temporal_coverage

    def _handle_distribution(self, resources, doi):
        distrs = []
        if doi.startswith("10.16904"):
            distrs.append(
                {
                    self.type_tag: "DataDownload",
                    self.content_url_tag: f"https://envidat-doi.os.zhdk.cloud.switch.ch/?prefix={doi.replace('/', '_')}",
                    self.name_tag: "S3 URI",
                }
            )

        resource_mapping_file = requests.get("https://os.zhdk.cloud.switch.ch/envidat-doi/_info/resource_mapping.csv")
        reader = csv.DictReader(StringIO(resource_mapping_file.text))
        resource_mapping = {}
        for row in reader:
            if row and row.get('doi') == doi:
                resource_mapping[row.get("id")] = row.get("name")

        for resource in resources:
            # We discussed that the URL should point to the copy in the envidat-doi bucket if it's an S3 bucket.
            # Once this is done we can delete this:
            # vvv
            rs_url = resource.get("url")
            base = f"https://envidat-doi.os.zhdk.cloud.switch.ch/?prefix={doi.replace('/', '_')}"
            if rs_url.startswith("https://os.zhdk.cloud.switch.ch/envicloud"):
                namespace = {"ns": "http://s3.amazonaws.com/doc/2006-03-01/"}
                url = base
                while True:
                    response = get(url, timeout=10)
                    if response.status_code != 200:
                        raise Exception(f"Error fetching data: {response.status_code}")
                    content = response.text
                    root = ET.fromstring(content)

                    for item in root.findall("ns:Contents", namespace):
                        key_element = item.find("ns:Key", namespace).text

                        if key_element.count("/") > 1:
                            parts = key_element.split("/")
                            rs_url = f"{base}/{parts[1]}"
                            break

                    nextMarker = root.find("ns:NextMarker", namespace)
                    if nextMarker is not None:
                        url = f"{base}&marker={nextMarker.text}"
                    else:
                        break
            # ^^^

            if resource.get("id") in resource_mapping:
                rs_url = "https://os.zhdk.cloud.switch.ch/envidat-doi/" + doi.replace("/", "_") + "/" + resource_mapping[resource.get("id")]

            #if mapping exists: rs_url = is base URL + doi + file name
            #if mapping doesnt exist: continue as usual
            #
            distr = {
                self.type_tag: "DataDownload",
                self.content_url_tag: rs_url,
                self.contentSize_tag: self._size_helper(
                    resource.get("size", ""), resource.get("resource_size", "")
                ),
                self.encoding_format_tag: encoding_format_helper(resource),
                self.name_tag: resource.get("name"),
            }

            distrs.append(distr)
        return distrs

    def _size_helper(self, size_value, resource_size_value):
        size = size_value
        if not size:
            size = resource_size_value
            if size:
                size = json.loads(size)
                unit = size.get("size_units", "")
                value = size.get("size_value", "")
                if value and unit:
                    size = float(value) * self.units[unit]
                else:
                    size = 0
            if not size:
                size = 0
        return int(size)

    def _handle_spatial(self, geojson_obj: str) -> dict:
        """
        Convert a GeoJSON geometry into a Science-on-Schema.org 'spatialCoverage' dict.

        Returns JSON-LD with @type=Place and either:
          - GeoCoordinates (for a Point)
          - GeoShape (for Polygon, LineString, etc.) that consists of a bounding box

        Args:
            geojson_obj: A GeoJSON string or dict.

        Returns:
            dict: A "spatialCoverage" JSON-LD compatible object.
        """
        spatial_coverage = {}

        # Parse string input
        if isinstance(geojson_obj, str):
            try:
                geojson_obj = json.loads(geojson_obj)
            except json.JSONDecodeError:
                print(f"Invalid 'spatial' GeoJSON string: {geojson_obj}")
                return spatial_coverage

        # Validate structure
        if not isinstance(geojson_obj, dict) or "type" not in geojson_obj:
            print(f"Invalid GeoJSON structure: {geojson_obj}")
            return spatial_coverage

        try:
            geom = shape(geojson_obj)
        except Exception as e:
            print(f"Invalid geometry: {e}")
            return spatial_coverage

        spatial_coverage: dict[str, Any] = {
            "@type": "Place",
            "geo": {}
        }

        # Handle each geometry type
        geom_type = geom.geom_type

        if geom_type == "Point":
            lon, lat = geom.coords[0]
            spatial_coverage["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": lat,
                "longitude": lon
            }

        else:
            # Compute bounding box for Polygon, LineString, Multi*, etc.
            minx, miny, maxx, maxy = geom.bounds
            spatial_coverage["geo"] = {
                "@type": "GeoShape",
                "box": f"{miny} {minx} {maxy} {maxx}"
            }

        return spatial_coverage

    def _handle_license(
            self,
            doi: str,
            license_id: str,
            license_url: str | None = None
    ) -> list[str] | str:
        """
        Return a list of strings with licenses:
            - The first item is the SPDX URL
            - The second item is the URL in EnviDat's 'license_url' field

        If there is no corresponding SPDX URL then return the DOI URL or a link to the
        WSL data policy.

        To learn more about SPDX licenses see:
        https://spdx.org/licenses

        Args:
            doi: Value of EnviDat field 'doi'
            license_id: Value of EnviDat field 'license_id'
            license_url: Value of EnviDat field 'license_url' if it exists (else None)
        """
        if spdx_url := self.license_spdx.get(license_id):
            if license_url:
                return [spdx_url, license_url]
            else:
                return spdx_url

        elif license_id == "wsl-data":
            return self.wsl_data_license_url

        else:
            return f"{self.doi_url}{doi}"

    def _handle_citation(
            self,
            doi: str,
            related_publications: str | None = None
    ) -> str:
        """
        Return a full DOI link corresponding to the first DOI found in
        EnviDat field 'related_publications'.

        If no DOI found in 'related_publications' then return the first line of that
        EnviDat field value.

        Else return the dataset's DOI URL.

        Args:
            doi: Value of EnviDat field 'doi'
            related_publications: Value of EnviDat field 'related_publications'
        """
        if not related_publications:
            return f"{self.doi_url}{doi}"

        lines = [
            ln.strip()
            for ln in related_publications.splitlines()
            if ln.strip()
        ]

        for ln in lines:

            ln_words = ln.split(" ")

            for word in ln_words:
                if word.startswith(self.doi_url) and len(word) > len(self.doi_url):
                    return word
                elif word.startswith("doi:"):
                    if doi_value := word.split("doi:")[-1]:
                        return f"{self.doi_url}{doi_value}"

        if lines:
            return lines[0]

        return f"{self.doi_url}{doi}"
