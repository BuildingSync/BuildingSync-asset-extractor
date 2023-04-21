import logging
from typing import Any, Callable, Optional, Tuple, Union

from buildingsync_asset_extractor.converter import unify_units
from buildingsync_asset_extractor.eletric_fuel_types import electric_fuel_types
from buildingsync_asset_extractor.lighting_processing.lighting_processing import (
    LightingData,
    LightingDataLPD,
    LightingDataPower
)
from buildingsync_asset_extractor.types import SystemData

# Gets or creates a logger
logging.basicConfig()
logger = logging.getLogger(__name__)

# set log level
logger.setLevel(logging.DEBUG)


class Formatter():
    """These functions take in processed data, calucates the asset and it's unit, then exports it.
    """
    def __init__(self, export_asset: Callable[[str, Any], None], export_asset_units: Callable[[str, Any], None]):
        self.export_asset = export_asset
        self.export_asset_units = export_asset_units

    def format_age_results(self, name: str, results: list[SystemData], process_type: str, units: Optional[str]) -> None:
        # process results
        value = None
        if process_type.endswith('oldest'):
            res_vals = [sub.value for sub in results]
            s_res = sorted(res_vals)
            if s_res:
                value = s_res[0]

            self.export_asset(name, str(value))
            self.export_asset_units(name, units)

        elif process_type.endswith('newest'):
            res_vals = [sub.value for sub in results]
            s_res = sorted(res_vals, reverse=True)
            if s_res:
                value = s_res
            self.export_asset(name, str(value))
            self.export_asset_units(name, units)

        elif process_type.endswith('average'):
            self.format_custom_avg_results(name, results, units)

    def format_80_percent_results(self, name: str, results: list[SystemData], units: Optional[str]) -> None:
        """ format 80% rule results
            the "primary" type returned must at least serve 80% of the area by
            1. Capacity
            2. Served space area
        """
        if len(results) == 0:
            # export None
            self.export_asset(name, None)
            self.export_asset_units(name, units)
            return

        # if only 1 asset, we'll call it primary!
        if len(results) == 1:
            self.export_asset(name, results[0].value)
            self.export_asset_units(name, units)
            return

        results = unify_units(results)

        values, capacities, cap_units, sqfts = self.remap_results(results)
        if None not in capacities and len(set(cap_units)) <= 1:
            # capacity method
            # add all capacities
            # pick largest one and make sure it's 80% of total
            found = 0
            total = sum(capacities)  # type: ignore
            if total > 0:
                primaries = {}
                for res in results:
                    if res.value not in primaries:
                        primaries[res.value] = 0.0
                    primaries[res.value] += float(res.cap)  # type: ignore

                for p in primaries:
                    if float(primaries[p])/total >= 0.8:
                        # this fuel meets the 80% threshold by capacity
                        found = 1
                        self.export_asset(name, p)
                        self.export_asset_units(name, units)
                        return

            if found == 0:
                # nothing matched this criteria, return 'Mixed'
                self.export_asset(name, 'mixed')
                self.export_asset_units(name, units)
                return

        if None not in sqfts:
            # sqft method
            total = sum(sqfts)  # type: ignore
            found = 0
            if total > 0:
                primaries = {}
                for res in results:
                    if res.value not in primaries:
                        primaries[res.value] = 0
                    if res.sqft is not None:
                        primaries[res.value] += res.sqft

                for p in primaries:
                    if float(primaries[p])/total >= 0.8:
                        # this fuel meets the 80% threshold by capacity
                        found = 1
                        self.export_asset(name, p)
                        self.export_asset_units(name, units)
                        return

            if found == 0:
                # nothing matched this criteria, return 'Mixed'
                self.export_asset(name, 'mixed')
                self.export_asset_units(name, units)
                return

        # still here? return unknown
        self.export_asset(name, 'unknown')
        self.export_asset_units(name, units)
        return

    def format_lighting_results(self, name: str, results: list[LightingData], units: Optional[str]) -> None:
        """ custom processing for lighting efficiency
            1. if 'lpd' is present, average the values
            2. else if percentpremisesserved
            3. otherwise regular sqft
        """
        if len(results) == 0:
            # export None, no units
            self.export_asset(name, None)
            self.export_asset_units(name, units)
            return

        # check method 1
        has_lpd = all([isinstance(r, LightingDataLPD) for r in results])

        # for weighted average, re-find Watts from LPD and LinkedPremises and divide by total sqft
        if has_lpd:
            value = 0.0
            total_sqft = 0.0
            for r in results:
                value += r.lpd * r.sqft  # type: ignore # TODO: remove.
                total_sqft += r.sqft
            if value > 0:
                value = value / total_sqft

            self.export_asset(name, value)
            self.export_asset_units(name, units)
            return

        # check method 2
        # need both PercentPremises AND LinkedPremises for this
        # running sum of all watts / running sum of all fractions of sqft
        has_perc = all([r.sqft_percent is not None for r in results])
        has_power = all([isinstance(r, LightingDataPower) for r in results])
        if has_perc and has_power:
            power = 0
            sqft_total = 0.0
            for r in results:
                power += r.power  # type: ignore
                sqft_total = r.sqft_percent / 100 * r.sqft  # type: ignore
            if power > 0:
                value = power / sqft_total
            self.export_asset(name, value)
            self.export_asset_units(name, units)
            return

        # check method 3
        sqfts = [sub.sqft if sub.sqft is None else float(sub.sqft) for sub in results]
        if None not in sqfts and has_power:
            # sqft methods
            remapped_power = [sub.power for sub in results]  # type: ignore
            remapped_sqft = [sub.sqft for sub in results]
            top = sum(remapped_power)
            bottom = sum(remapped_sqft)
            if bottom > 0:
                value = top / bottom
                self.export_asset(name, value)
                self.export_asset_units(name, units)
                return

        # can't calculate
        self.export_asset(name, 'unknown')
        self.export_asset_units(name, units)
        return

    def format_custom_avg_results(self, name: str, results: list[SystemData], units: Optional[str]) -> None:
        """ format weighted average
            1. Ensure all units are the same
            2. Attempt to calculate with installed power (NOT IMPLEMENTED)
            3. Attempt to calculate with capacity (cap)
            4. Attempt to calculate with served space area (sqrt)
            Don't export units for 'average age' (review this in the future)
        """

        if len(results) == 0:
            # export None, no units
            self.export_asset(name, None)
            self.export_asset_units(name, units)
            return

        # 1. units
        if units == 'mixed':
            self.export_asset(name, 'mixed')
            self.export_asset_units(name, units)
            return

        results = unify_units(results)

        values, capacities, cap_units, sqfts = self.remap_results(results)

        # logger.debug(f"values: {values}")
        # logger.debug(f"capacities: {capacities}")
        # logger.debug(f"length: {len(set(cap_units)) <= 1}")

        # 2 - capacity
        # check that there are capacities for all and the units are all the same
        if None not in capacities and len(set(cap_units)) == 1:
            # capacity methods
            cap_total = 0.0
            eff_total = 0.0
            for res in results:
                cap_total = cap_total + float(res.cap)  # type: ignore
                eff_total = eff_total + (float(res.value) * float(res.cap))  # type: ignore
            total: Union[float, str] = eff_total / cap_total

            # special case for average age: take the floor since partial year doesn't make sense
            if name.lower().endswith('age'):
                total = str(int(total))

            self.export_asset(name, total)
            self.export_asset_units(name, units)
            return

        elif None not in sqfts:
            # sqft methods
            remapped_res = {sub.value: sub.sqft for sub in results}
            self.format_avg_sqft_results(name, remapped_res, units)  # type: ignore
            return
        else:
            # just average
            total = sum(values)/len(values)  # type: ignore
            # special case for average age: take the floor since partial year doesn't make sense
            if name.lower().endswith('age'):
                total = int(total)
            self.export_asset(name, total)
            self.export_asset_units(name, units)
            return

    def format_sqft_results(self, name: str, results: dict[str, float], units: Optional[str]) -> None:
        """ return primary and secondary for top 2 results by sqft """
        # NOTE: this is the only method that modifies the export name '
        # by appending 'primary' and 'secondary'
        # no units associated with this now

        # filter and sort results
        filtered_res = {k: v for k, v in results.items() if v != 0}
        s_res = dict(sorted(filtered_res.items(), key=lambda kv: kv[1], reverse=True))
        logger.debug('sorted results with zeros removed: {}'.format(s_res))

        value = None
        value2 = None

        s_keys = list(s_res.keys())
        if s_keys:
            value = s_keys[0]
        self.export_asset('Primary ' + name, value)
        self.export_asset_units('Primary ' + name, units)

        if (len(s_keys) > 1):
            value2 = s_keys[1]
        self.export_asset('Secondary ' + name, value2)
        self.export_asset_units('Secondary ' + name, units)

    def format_avg_sqft_results(self, name: str, results: dict[Any, float], units: Optional[str]) -> None:
        """ weighted average of results """

        # in this case the result keys will convert to numbers
        # to calculate the weighted average

        total: Union[str, float, None] = None

        if results:
            total_sqft = sum(results.values())

            running_sum = 0.0
            for k, v in results.items():
                running_sum += float(k) * v
            if running_sum > 0 and total_sqft > 0:
                total = running_sum / total_sqft

        # special case for average age: take the floor since partial year doesn't make sense
        if name.lower().endswith('age') and total is not None:
            total = str(int(total))

        # add to assets
        self.export_asset(name, total)
        self.export_asset_units(name, units)

    def format_electrification_pontential(self, name: str, results: list[SystemData], units: Optional[str]) -> None:
        """Sum non electric capacites"""
        # If no SystemDatas, then None
        if len(results) == 0:
            self.export_asset(name, None)
            self.export_asset_units(name, units)
            return

        non_electric = [
            sd for sd in results
            if sd.value not in electric_fuel_types
            and sd.cap is not None
        ]

        # if no non electric SystemDatas, then 0
        if len(non_electric) == 0:
            self.export_asset(name, 0)
            self.export_asset_units(name, units)
            return

        # try to convert cap to same power unit
        if not units:
            units = non_electric[0].cap_units
        non_electric = unify_units(non_electric, to_units=units)

        # if all non electric SystemData have same cap unit, sum
        _, capacities, cap_units, _ = self.remap_results(non_electric)
        if len(set(cap_units)) <= 1:
            self.export_asset(name, sum([c for c in capacities if c is not None]))
            self.export_asset_units(name, cap_units[0])
            return

        # else unknown
        self.export_asset(name, 'unknown')
        self.export_asset_units(name, None)
        return

    def remap_results(self, results: list[SystemData]) -> \
            Tuple[list[Optional[float]], list[Optional[float]], list[Optional[str]], list[Optional[float]]]:
        """ Remap results from a list of dictionaries to 4 lists """
        try:
            values = [sub.value if sub.value is None else float(sub.value) for sub in results]
        except ValueError:
            values = [sub.value for sub in results]

        capacities = [sub.cap if sub.cap is None else float(sub.cap) for sub in results]
        cap_units = [sub.cap_units for sub in results]
        sqfts = [sub.sqft if sub.sqft is None else float(sub.sqft) for sub in results]

        return values, capacities, cap_units, sqfts
