#!/usr/env/bin python3
"""Read and process files from the catalog releases"""
######## Imports ########
#### Standard Library ####
from abc import ABC, abstractmethod
from os import path, getcwd, chdir, remove, rename, system as command
from functools import cache
import warnings
#### Third Party ####
import numpy as np
#### Homemade ####
from xdata import Database
#### Local ####
from gwalk.data.registry import GwalkFileRegistry as Registry
from gwalk.catalog.coordinates import coordinate_aliases, coordinate_lambdas, coordinate_tags
from gwalk.catalog.prior.prior_methods import prior_mc_eta as prior_mass
from gwalk.catalog.prior.prior_methods import prior_dist
from gwalk.catalog.prior.prior_methods import prior_full_spin
from gwalk.catalog.prior.callister_prior import chi_effective_prior_of_aligned_spins as chi_eff_aligned_prior
from gwalk.mixture import KernelDensityEstimator

# Setup
WAVEFORM_ALIAS = {
    "PublicationSamples"                        : "PublicationSamples",
    "IMRPhenomPv2_posterior"                    : "IMRPhenomPv2",
    "SEOBNRv3_posterior"                        : "SEOBNRv3",
    "Overall_posterior"                         : "Overall",
    "IMRPhenomPv2NRT_highSpin_posterior"        : "IMRPhenomPv2NRT_highSpin",
    "IMRPhenomPv2NRT_lowSpin_posterior"         : "IMRPhenomPv2NRT_lowSpin",
    "PrecessingSpinIMRHM"                       : "PrecessingSpinIMRHM",
    "C01:IMRPhenomD"                            : "IMRPhenomD",
    "C01:IMRPhenomPv2"                          : "IMRPhenomPv2",
    "C01:SEOBNRv4P"                             : "SEOBNRv4P",
    "C01:SEOBNRv4PHM"                           : "SEOBNRv4PHM",
    "C01:IMRPhenomHM"                           : "IMRPhenomHM",
    "C01:IMRPhenomPv3HM"                        : "IMRPhenomPv3HM",
    "C01:SEOBNRv4HM_ROM"                        : "SEOBNRv4HM_ROM",
    "C01:SEOBNRv4_ROM"                          : "SEOBNRv4_ROM",
    "C01:NRSur7dq4"                             : "NRSur7dq4",
    "C01:SEOBNRv4P_nonevol"                     : "SEOBNRv4P_nonevol",
    "C01:IMRPhenomD_NRTidal-HS"                 : "IMRPhenomD_NRTidal-HS",
    "C01:IMRPhenomD_NRTidal-LS"                 : "IMRPhenomD_NRTidal-LS",
    "C01:IMRPhenomPv2_NRTidal-HS"               : "IMRPhenomPv2_NRTidal-HS",
    "C01:IMRPhenomPv2_NRTidal-LS"               : "IMRPhenomPv2_NRTidal-LS",
    "C01:SEOBNRv4T_surrogate_HS"                : "SEOBNRv4T_surrogate_HS",
    "C01:SEOBNRv4T_surrogate_LS"                : "SEOBNRv4T_surrogate_LS",
    "C01:SEOBNRv4T_surrogate_highspin_RIFT"     : "SEOBNRv4T_surrogate_highspin_RIFT",
    "C01:SEOBNRv4T_surrogate_lowspin_RIFT"      : "SEOBNRv4T_surrogate_lowspin_RIFT",
    "C01:TEOBResumS-HS"                         : "TEOBResumS-HS",
    "C01:TEOBResumS-LS"                         : "TEOBResumS-LS",
    "C01:TaylorF2-HS"                           : "TaylorF2-HS",
    "C01:TaylorF2-LS"                           : "TaylorF2-LS",
    "C01:IMRPhenomNSBH"                         : "IMRPhenomNSBH",
    "C01:TaylorF2"                              : "TaylorF2",
    "C01:SEOBNRv4P_RIFT"                        : "SEOBNRv4P_RIFT",
    "C01:IMRPhenomXPHM"                         : "IMRPhenomXPHM",
    "C01:Mixed"                                 : "Mixed",
    "C01:IMRPhenomNSBH:HighSpin"                : "IMRPhenomNSBH_HighSpin",
    "C01:IMRPhenomNSBH:LowSpin"                 : "IMRPhenomNSBH_LowSpin",
    "C01:IMRPhenomXPHM:HighSpin"                : "IMRPhenomXPHM_HighSpin",
    "C01:IMRPhenomXPHM:LowSpin"                 : "IMRPhenomXPHM_LowSpin",
    "C01:Mixed:NSBH:HighSpin"                   : "Mixed_NSBH_HighSpin",
    "C01:Mixed:NSBH:LowSpin"                    : "Mixed_NSBH_LowSpin",
    "C01:SEOBNRv4_ROM_NRTidalv2_NSBH"           : "SEOBNRv4_ROM_NRTidalv2_NSBH",
    "C01:SEOBNRv4_ROM_NRTidalv2_NSBH:HighSpin"  : "SEOBNRv4_ROM_NRTidalv2_NSBH_HighSpin",
    "C01:SEOBNRv4_ROM_NRTidalv2_NSBH:LowSpin"   : "SEOBNRv4_ROM_NRTidalv2_NSBH_LowSpin",
    "C00:IMRPhenomTPHM"                         : "IMRPhenomTPHM",
    "C00:IMRPhenomXO4a"                         : "IMRPhenomX04a",
    "C00:IMRPhenomXPHM-SpinTaylor"              : "IMRPhenomXPHM-SpinTaylor",
    "C00:Mixed"                                 : "Mixed",
    "C00:Mixed+XO4a"                            : "Mixed+XO4a",
    "C00:Mixed:HighSpin"                        : "Mixed-HighSpin",
    "C00:Mixed:LowSpin"                         : "Mixed-LowSpin",
    "C00:NRSur7dq4"                             : "NRSur7dq4",
    "C00:SEOBNRv5PHM"                           : "SEOBNRv5PHM",
    "C00:IMRPhenomNSBH:LowSpin"                 : "IMRPhenomNSBH-LowSpin",
    "C00:IMRPhenomPv2-NRTidalv2:LowSpin"        : "IMRPhenomPv2-NRTidalv2-LowSpin",
    "Bilby:NRSur7dq4"                           : "NRSur7dq4",
    "ZeroSpinIMR"                               : "ZeroSpinIMR",
    "PrecessingSpinIMR"                         : "PrecessingSpinIMR",
    "AlignedSpinIMR"                            : "AlignedSpinIMR",
    "AlignedSpinIMRHM"                          : "AlignedSpinIMRHM",
}

WAVEFORMS_BEST = [
    "NRSur7dq4",
    "SEOBNRv5PHM",
    "SEOBNRv4PHM",
    "IMRPhenomXPHM",
    "IMRPhenomPv3",
    "SEOBNRv3",
    "IMRPhenomPv2NRT_lowSpin",
    "Mixed-HighSpin",
    "PublicationSamples",
]

EVENTS = {
    "GWTC-1" : [
        "GW150914",
        "GW151012",
        "GW151226",
        "GW170104",
        "GW170608",
        "GW170729",
        "GW170809",
        "GW170814",
        "GW170817",
        "GW170818",
        "GW170823",
    ],
    "GWTC-2" : [
        'GW190408_181802',
        'GW190412',
        'GW190413_052954',
        'GW190413_134308',
        'GW190421_213856',
        'GW190424_180648',
        'GW190425',
        'GW190426_152155',
        'GW190503_185404',
        'GW190512_180714',
        'GW190513_205428',
        'GW190514_065416',
        'GW190517_055101',
        'GW190519_153544',
        'GW190521',
        'GW190521_074359',
        'GW190527_092055',
        'GW190602_175927',
        'GW190620_030421',
        'GW190630_185205',
        'GW190701_203306',
        'GW190706_222641',
        'GW190707_093326',
        'GW190708_232457',
        'GW190719_215514',
        'GW190720_000836',
        'GW190727_060333',
        'GW190728_064510',
        'GW190731_140936',
        'GW190803_022701',
        'GW190814',
        'GW190828_063405',
        'GW190828_065509',
        'GW190909_114149',
        'GW190910_112807',
        'GW190915_235702',
        'GW190924_021846',
        'GW190929_012149',
        'GW190930_133541',
    ],
    "GWTC-2p1" : [
          "GW150914_095045",
          "GW151012_095443",
          "GW151226_033853",
          "GW170104_101158",
          "GW170608_020116",
          "GW170729_185629",
          "GW170809_082821",
          "GW170814_103043",
          "GW170818_022509",
          "GW170823_131358",
          "GW190403_051519",
          "GW190408_181802",
          "GW190412_053044",
          "GW190413_052954",
          "GW190413_134308",
          "GW190421_213856",
          "GW190425_081805",
          "GW190426_190642",
          "GW190503_185404",
          "GW190512_180714",
          "GW190513_205428",
          "GW190514_065416",
          "GW190517_055101",
          "GW190519_153544",
          "GW190521_030229",
          "GW190521_074359",
          "GW190527_092055",
          "GW190602_175927",
          "GW190620_030421",
          "GW190630_185205",
          "GW190701_203306",
          "GW190706_222641",
          "GW190707_093326",
          "GW190708_232457",
          "GW190719_215514",
          "GW190720_000836",
          "GW190725_174728",
          "GW190727_060333",
          "GW190728_064510",
          "GW190731_140936",
          "GW190803_022701",
          "GW190805_211137",
          "GW190814_211039",
          "GW190828_063405",
          "GW190828_065509",
          "GW190910_112807",
          "GW190915_235702",
          "GW190916_200658",
          "GW190917_114630",
          "GW190924_021846",
          "GW190925_232845",
          "GW190926_050336",
          "GW190929_012149",
          "GW190930_133541",
    ],
    "GWTC-3" : [
          "GW191103_012549",
          "GW191105_143521",
          "GW191109_010717",
          "GW191113_071753",
          "GW191126_115259",
          "GW191127_050227",
          "GW191129_134029",
          "GW191204_110529",
          "GW191204_171526",
          "GW191215_223052",
          "GW191216_213338",
          "GW191219_163120",
          "GW191222_033537",
          "GW191230_180458",
          "GW200105_162426",
          "GW200112_155838",
          "GW200115_042309",
          "GW200128_022011",
          "GW200129_065458",
          "GW200202_154313",
          "GW200208_130117",
          "GW200208_222617",
          "GW200209_085452",
          "GW200105_162426",
          "GW200112_155838",
          "GW200115_042309",
          "GW200128_022011",
          "GW200129_065458",
          "GW200202_154313",
          "GW200208_130117",
          "GW200208_222617",
          "GW200209_085452",
          "GW200210_092254",
          "GW200216_220804",
          "GW200219_094415",
          "GW200220_061928",
          "GW200220_124850",
          "GW200224_222234",
          "GW200225_060421",
          "GW200302_015811",
          "GW200306_093714",
          "GW200308_173609",
          "GW200311_115853",
          "GW200316_215756",
          "GW200322_091133",
    ],
    "GWTC-4" : [
        "GW230518_125908",
        "GW230529_181500",
        "GW230601_224134",
        "GW230605_065343",
        "GW230606_004305",
        "GW230608_205047",
        "GW230609_064958",
        "GW230624_113103",
        "GW230627_015337",
        "GW230628_231200",
        "GW230630_125806",
        "GW230630_234532",
        "GW230702_185453",
        "GW230704_021211",
        "GW230704_212616",
        "GW230706_104333",
        "GW230707_124047",
        "GW230708_053705",
        "GW230708_230935",
        "GW230709_122727",
        "GW230712_090405",
        "GW230723_101834",
        "GW230726_002940",
        "GW230729_082317",
        "GW230731_215307",
        "GW230803_033412",
        "GW230805_034249",
        "GW230806_204041",
        "GW230811_032116",
        "GW230814_061920",
        "GW230814_230901",
        "GW230819_171910",
        "GW230820_212515",
        "GW230824_033047",
        "GW230825_041334",
        "GW230831_015414",
        "GW230904_051013",
        "GW230911_195324",
        "GW230914_111401",
        "GW230919_215712",
        "GW230920_071124",
        "GW230922_020344",
        "GW230922_040658",
        "GW230924_124453",
        "GW230927_043729",
        "GW230927_153832",
        "GW230928_215827",
        "GW230930_110730",
        "GW231001_140220",
        "GW231004_232346",
        "GW231005_021030",
        "GW231005_091549",
        "GW231008_142521",
        "GW231014_040532",
        "GW231018_233037",
        "GW231020_142947",
        "GW231028_153006",
        "GW231029_111508",
        "GW231102_071736",
        "GW231104_133418",
        "GW231108_125142",
        "GW231110_040320",
        "GW231113_122623",
        "GW231113_200417",
        "GW231114_043211",
        "GW231118_005626",
        "GW231118_071402",
        "GW231118_090602",
        "GW231119_075248",
        "GW231123_135430",
        "GW231127_165300",
        "GW231129_081745",
        "GW231206_233134",
        "GW231206_233901",
        "GW231213_111417",
        "GW231221_135041",
        "GW231223_032836",
        "GW231223_075055",
        "GW231223_202619",
        "GW231224_024321",
        "GW231226_101520",
        "GW231230_170116",
        "GW231231_154016",
        "GW240104_164932",
        "GW240107_013215",
        "GW240109_050431",
    ],
    "NRSurCat-1" : [
        "GW150914_095045",
        "GW170729_185629",
        "GW170809_082821",
        "GW170818_022509",
        "GW170823_131358",
        "GW190413_052954",
        "GW190413_134308",
        "GW190421_213856",
        "GW190426_190642",
        "GW190503_185404",
        "GW190513_205428",
        "GW190514_065416",
        "GW190517_055101",
        "GW190519_153544",
        "GW190521_030229",
        "GW190521_074359",
        "GW190527_092055",
        "GW190602_175927",
        "GW190620_030421",
        "GW190630_185205",
        "GW190701_203306",
        "GW190706_222641",
        "GW190727_060333",
        "GW190731_140936",
        "GW190803_022701",
        "GW190805_211137",
        "GW190828_063405",
        "GW190910_112807",
        "GW190915_235702",
        "GW190916_200658",
        "GW190926_050336",
        "GW190929_012149",
        "GW191109_010717",
        "GW191222_033537",
        "GW191230_180458",
        "GW200112_155838",
        "GW200128_022011",
        "GW200129_065458",
        "GW200208_130117",
        "GW200209_085452",
        "GW200216_220804",
        "GW200219_094415",
        "GW200220_061928",
        "GW200220_124850",
        "GW200224_222234",
        "GW200302_015811",
        "GW200311_115853",
    ]
}


######## Functions ########
######## EventCatalog Object ########
class EventCatalog(ABC):
    """Class for GW Event PE release files"""
    def __init__(self, event):
        """Initialize catalog object for a given event

        Inputs
        ------
        event : str
            Phone number for event (GW231123)
        """
        self.event = event
        self.registry = Registry()

    #### Properties specific to each catalog ####
    @property
    @abstractmethod
    def catalog(self) -> str:
        pass
    @property
    def catalog_events(self):
        return EVENTS[self.catalog]

    @property
    @abstractmethod
    def basename(self) -> str:
        pass
    @property
    @abstractmethod
    def basename_h5(self) -> str:
        pass
    @property
    @abstractmethod
    def basename_raw(self) -> str:
        pass
    @property
    @abstractmethod
    def url(self) -> str:
        pass
    @property
    def fname(self) -> str:
        return path.join(self.registry.directory, self.basename_h5)
    @property
    @abstractmethod
    def waveform_group(self):
        pass
    @abstractmethod
    def dset_addr(self, wav):
        pass


    #### Registry methods ####
    @property
    def is_hashed(self):
        return self.registry.is_hashed(self.basename_raw)

    def validate(self):
        self.registry.validate(path.join(self.registry.directory,self.basename_raw))

    @property
    def bytesize(self):
        """Return the size of the PE sample file"""
        hash_dict = self.registry.load_hash(self.basename_raw)
        return hash_dict["bytesize"]

    def remove(self):
        self.registry.remove(self.basename_raw, assume_yes=True)

    def download(self):
        """Download the event"""
        self.registry.download(self.url, assume_yes=True)

    def spider(self):
        """Check if the event really exists"""
        self.registry.download(self.url, spider=True)
            
    def save(self):
        if self.is_hashed:
            self.registry.update_hash(path.join(self.registry.directory,self.basename_raw))
        else:
            self.registry.save_hash(path.join(self.registry.directory,self.basename_raw))

    #### Database methods ####
    @property
    @cache
    def db(self):
        if not path.isfile(self.fname):
            raise RuntimeError(f"No such file: {self.fname}")
        return Database(self.fname)

    @property
    @cache
    def waveforms(self):
        wav = []
        for item in self.db.list_items(self.waveform_group):
            # Skip things that are not PE samples
            if item in ["history", "version"]:
                continue
            # Check aliases
            if item in WAVEFORM_ALIAS:
                wav.append(WAVEFORM_ALIAS[item])
            elif item.endswith("prior"):
                continue
            else:
                warnings.warn(f"Unknown waveform? {item}")
        return wav

    def field_tuple(self, wav):
        """Load the field_tuple of the dataset"""
        # Get address of dataset
        addr = self.dset_addr(wav)
        # Get fields
        return self.db.dset_fields(addr)

    def fields(self, wav):
        """Load the names of each field"""
        # Initialize list
        field_list = []
        # iterate field_tuple
        for ftup in self.field_tuple(wav):
            field_list.append(ftup)
        return field_list

    def load_samples(self,wav,key,indices=None):
        """Load samples from a particular field"""
        if wav not in self.waveforms:
            raise ValueError(f"key {wav} not in {__class__}.waveforms for {self.event}")
        if key not in self.fields(wav):
            raise ValueError(f"key {key} not in {__class__}.fields for {self.event} with {wav}")
        return self.db.dset_value(self.dset_addr(wav),samples=indices,field=key)

    def find_samples(self,wav,key,indices=None):
        """Load samples if available, but also check for aliases and construction
        """
        # Check the waveform
        if wav not in self.waveforms:
            raise ValueError(f"key {wav} not in {__class__}.waveforms for {self.event}")
        # If the samples are available just grab them
        if key in self.fields(wav):
            return self.load_samples(wav,key,indices=indices)
        # Check if key is in coordinate_aliases
        elif (key in list(coordinate_aliases.values())) and \
                (next((alias for alias, value in coordinate_aliases.items() if value == key), False) in self.fields(wav)):
            for alias in coordinate_aliases:
                if coordinate_aliases[alias] == key:
                   return self.load_samples(wav,alias,indices=indices)
        # Else check if it's in coordinate_lambdas
        elif key in coordinate_lambdas:
            components, func = coordinate_lambdas[key]
            samples = []
            for comp in components:
                samples.append(self.find_samples(wav,comp,indices=indices))
            return func(*samples)
        else:
            print("fields:")
            print(self.fields(wav))
            print("all aliases:")
            for alias, value in coordinate_aliases.items():
                print(alias, value)
            print(f"all lambdas:")
            for alias, value in coordinate_lambdas.items():
                print(alias, value)
            print("all coordinate_tags:")
            for alias, value in coordinate_tags.items():
                print(alias, value)
            raise ValueError(f"Trouble finding {key} in {wav} for {self.event}")

    def can_find_samples(self,wav,key):
        """Check if finding samples for a particular coordinate/waveform is possible
        """
        # Check that waveform is real
        if wav not in self.waveforms:
            return False
        # Check if samples are just there
        if key in self.fields(wav):
            return True
        # Check if key is in coordinate_aliases
        elif (key in list(coordinate_aliases.values())) and \
                (next((alias for alias, value in coordinate_aliases.items() if value == key), False) in self.fields(wav)):
            for alias in coordinate_aliases:
                if coordinate_aliases[alias] == key:
                    return True
            return False
        # Else check if it's in coordinate_lambdas
        elif key in coordinate_lambdas:
            components, func = coordinate_lambdas[key]
            found = True
            for comp in components:
                found = found and self.can_find_samples(wav,comp)
            if found:
                return True
        return False

    def has_coordinate_tag(self,wav,tag):
        """Return True if we can get all the samples for a coordinate tag;elseF
        """
        # Common sense
        if tag not in coordinate_tags:
            print("all coordinate_tags:")
            for alias, value in coordinate_tags.items():
                print(alias, value)
            raise ValueError(f"Unknown coordinate tag: {tag}")
        # Check on samples
        found = True
        for key in coordinate_tags[tag]:
            if not key.startswith("prior"):
                found = found & self.can_find_samples(wav,key)
        # Note: We're making an assumption here that our prior does not
        #   require samples we can't get
        # Return found
        return found

    def samples_nonsingular(self,wav,tag):
        """Return True if samples are nonsingular; False otherwise"""
        # Common sense
        if tag not in coordinate_tags:
            print("all coordinate_tags:")
            for alias, value in coordinate_tags.items():
                print(alias, value)
            raise ValueError(f"Unknown coordinate tag: {tag}")
        # Load samples
        samples = []
        for key in coordinate_tags[tag]:
            if not key.startswith("prior"):
                # Append samples
                samples.append(self.find_samples(wav,key))
        # Check if singular
        if any(np.std(samples,axis=1) == 0.):
            return False
        else:
            return True
        raise ValueError(f"This function should never have gotten here.")

    def waveform_tags(self,wav):
        """Return all of the coordinate tags available for a given waveform"""
        tags = []
        for tag in coordinate_tags:
            if self.has_coordinate_tag(wav,tag):
                tags.append(tag)
        return tags
            

    def coordinate_tag_samples(self,wav,tag,indices=None):
        # Common sense
        if tag not in coordinate_tags:
            print("all coordinate_tags:")
            for alias, value in coordinate_tags.items():
                print(alias, value)
            raise ValueError(f"Unknown coordinate tag: {tag}")
        # Load samples
        samples = []
        for key in coordinate_tags[tag]:
            if not key.startswith("prior"):
                # Append samples
                samples.append(self.find_samples(wav,key,indices=indices))
            else:
                # Calculate prior
                mc = self.find_samples(wav, "chirp_mass",indices=indices)
                eta = self.find_samples(wav, "symmetric_mass_ratio",indices=indices)
                mass_limits = np.asarray([
                    [0., np.max(mc)],
                    [1e-6,0.25],
                ])
                mass_prior = prior_mass(
                    mc, eta,
                    mc_min=mass_limits[0,0],
                    mc_max=mass_limits[0,1],
                    eta_min=mass_limits[1,0],
                    eta_max=mass_limits[1,1],
                )
                # Calculate distance prior
                if ("dist" in tag) or (tag in ["full_precessing_tides"]):
                    lum_dist = self.find_samples(wav, "luminosity_distance",indices=indices)
                    dist_prior = prior_dist(lum_dist)
                else:
                    dist_prior = np.ones_like(mass_prior)
                # Calculate spin prior
                if "aligned" in tag:
                    q = self.find_samples(wav,"mass_ratio",indices=indices)
                    chi_eff = self.find_samples(wav, "chi_eff",indices=indices)
                    spin_prior = chi_eff_aligned_prior(
                        q,
                        1.0,
                        chi_eff,
                    )
                elif ("precessing" in tag) or (tag in ["spin6d"]):
                    chi1x = self.find_samples(wav, "spin_1x",indices=indices)
                    chi1y = self.find_samples(wav, "spin_1y",indices=indices)
                    chi1z = self.find_samples(wav, "spin_1z",indices=indices)
                    chi2x = self.find_samples(wav, "spin_2x",indices=indices)
                    chi2y = self.find_samples(wav, "spin_2y",indices=indices)
                    chi2z = self.find_samples(wav, "spin_2z",indices=indices)
                    spin_prior = prior_full_spin(chi1x, chi2x, chi1y, chi2y, chi1z, chi2z)
                elif tag in ["mass_tides", "mass_tides_source"]:
                    spin_prior = np.ones_like(mass_prior)
                else:
                    raise RuntimeError(f"Unknown spin prior for coordinate tag {tag}!")
                    spin_prior = np.ones_like(mass_prior)
                # Assemble prior
                prior = mass_prior * dist_prior * spin_prior

        return np.column_stack(samples), prior
                    
    def coordinate_tag_kde(
            self,
            wav,
            tag,
            indices=None,
            limits=None,
            **kde_kwargs
        ):
        """Return a KDE for some samples"""
        # Load samples
        samples, prior = self.coordinate_tag_samples(wav,tag,indices=indices)
        # Initialize limits
        ndim = samples.shape[1]
        if limits is None:
            limits = np.empty((ndim,2),dtype=float)
            # Loop coordinates 
            for i in range(ndim):
                # Set limits from sample range
                limits[i,0] = np.min(samples[:,i])
                limits[i,1] = np.max(samples[:,i])
        # Generate KDE
        kde = KernelDensityEstimator(samples,limits,weights=prior**-1)
        return kde

        


#### Specific Filetypes ####
class GWTC_1_EventCatalog(EventCatalog):
    """Class for files at https://dcc.ligo.org/LIGO-P1800370/public"""
    events = EVENTS["GWTC-1"]
    @property
    def catalog(self) -> str:
        return "GWTC-1"
    @property
    def basename_h5(self) -> str:
        return f"{self.event}_GWTC-1.hdf5"
    @property
    def basename_raw(self) -> str:
        return self.basename_h5
    @property
    def basename(self) -> str:
        return self.basename_h5
    @property
    def waveform_group(self) -> str:
        return '.'
    # Dataset address
    def dset_addr(self, wav) -> str:
        if wav not in self.waveforms:
            raise ValueError(f"waveform {wav} not in waveforms: {self.waveforms}")
        addr = None
        for key in WAVEFORM_ALIAS:
            if not WAVEFORM_ALIAS[key] == wav:
                continue
            if self.db.exists(key,kind='dset'):
                addr = key
        if addr is None:
            self.db.scan()
            raise RuntimeError(f"{__class__.dset_addr} is not defined correctly")
        if not self.db.exists(addr,kind='dset'):
            raise RuntimeError(f"{__class__.dset_addr} is not defined correctly")
        return addr

    @property
    def url(self) -> str:
        return f"https://dcc.ligo.org/public/0157/P1800370/005/{self.basename}"

class GWTC_2_EventCatalog(EventCatalog):
    """Class for files at https://dcc.ligo.org/LIGO-P2000223/public"""
    events = EVENTS["GWTC-2"]
    @property
    def catalog(self) -> str:
        return "GWTC-2"
    @property
    def basename_h5(self) -> str:
        return f"{self.event}.h5"
    @property
    def basename_raw(self) -> str:
        return f"{self.event}.tar"
    @property
    def basename(self) -> str:
        return self.basename_h5
    @property
    def waveform_group(self) -> str:
        return '.'

    def download(self):
        super().download()
        if not path.isfile(self.fname):
            here = getcwd()
            chdir(self.registry.directory)
            cmd = f"tar -xvf {self.basename_raw}"
            print(cmd)
            command(cmd)
            chdir(here)
            rename(
                path.join(self.registry.directory,self.event,self.basename_h5),
                self.fname,
            )
            cmd=f"rm -rf {path.join(self.registry.directory,self.event)}"
            print(cmd)
            command(cmd)

    # Dataset address
    def dset_addr(self, wav) -> str:
        if wav not in self.waveforms:
            raise ValueError(f"waveform {wav} not in waveforms: {self.waveforms}")
        addr = None
        for key in WAVEFORM_ALIAS:
            if not WAVEFORM_ALIAS[key] == wav:
                continue
            if self.db.exists(path.join(key,'posterior_samples'),kind='dset'):
                addr = path.join(key,"posterior_samples")
        if addr is None:
            self.db.scan()
            raise RuntimeError(f"{__class__.dset_addr} is not defined correctly")
        if not self.db.exists(addr,kind='dset'):
            db.list_items(wav)
            raise RuntimeError(f"{__class__.dset_addr} is not defined correctly")
        return addr
    def remove(self):
        super().remove()
        remove(self.fname)

    @property
    def url(self) -> str:
        return f"https://dcc.ligo.org/public/0169/P2000223/007/{self.event}.tar"


class GWTC_3_EventCatalog(EventCatalog):
    """Class for files at https://zenodo.org/records/5546663"""
    events = EVENTS["GWTC-3"]
    @property
    def catalog(self) -> str:
        return "GWTC-3"
    @property
    def basename_h5(self) -> str:
        return f"IGWN-GWTC3p0-v2-{self.event}_PEDataRelease_mixed_nocosmo.h5"
    @property
    def basename_raw(self) -> str:
        return self.basename_h5
    @property
    def basename(self) -> str:
        return self.basename_h5
    @property
    def waveform_group(self) -> str:
        return '.'

    # Dataset address
    def dset_addr(self, wav) -> str:
        if wav not in self.waveforms:
            raise ValueError(f"waveform {wav} not in waveforms: {self.waveforms}")
        addr = None
        for key in WAVEFORM_ALIAS:
            if not WAVEFORM_ALIAS[key] == wav:
                continue
            if self.db.exists(path.join(key,'posterior_samples'),kind='dset'):
                addr = path.join(key,"posterior_samples")
        if addr is None:
            self.db.scan()
            raise RuntimeError(f"{__class__.dset_addr} is not defined correctly")
        if not self.db.exists(addr,kind='dset'):
            db.list_items(wav)
            raise RuntimeError(f"{__class__.dset_addr} is not defined correctly")
        return addr
    @property
    def url(self) -> str:
        return f"https://zenodo.org/records/8177023/files/IGWN-GWTC3p0-v2-{self.event}_PEDataRelease_mixed_nocosmo.h5"


class GWTC_2p1_EventCatalog(EventCatalog):
    """Class for files at https://zenodo.org/records/6513631"""
    events = EVENTS["GWTC-2p1"]
    @property
    def catalog(self) -> str:
        return "GWTC-2p1"
    @property
    def basename_h5(self) -> str:
        return f"IGWN-GWTC2p1-v2-{self.event}_PEDataRelease_mixed_nocosmo.h5"
    @property
    def basename_raw(self) -> str:
        return self.basename_h5
    @property
    def basename(self) -> str:
        return self.basename_h5
    @property
    def waveform_group(self) -> str:
        return '.'


    # Dataset address
    def dset_addr(self, wav) -> str:
        if wav not in self.waveforms:
            raise ValueError(f"waveform {wav} not in waveforms: {self.waveforms}")
        addr = None
        for key in WAVEFORM_ALIAS:
            if not WAVEFORM_ALIAS[key] == wav:
                continue
            if self.db.exists(path.join(key,'posterior_samples'),kind='dset'):
                addr = path.join(key,"posterior_samples")
        if addr is None:
            self.db.scan()
            raise RuntimeError(f"{__class__.dset_addr} is not defined correctly")
        if not self.db.exists(addr,kind='dset'):
            db.list_items(wav)
            raise RuntimeError(f"{__class__.dset_addr} is not defined correctly")
        return addr
    @property
    def url(self) -> str:
        return f"https://zenodo.org/records/6513631/files/IGWN-GWTC2p1-v2-{self.event}_PEDataRelease_mixed_nocosmo.h5"

class GWTC_4_EventCatalog(EventCatalog):
    """Class for files at https://zenodo.org/records/16053484"""
    events = EVENTS["GWTC-4"]
    @property
    def catalog(self) -> str:
        return "GWTC-4"
    @property
    def basename_h5(self) -> str:
        return f"IGWN-GWTC4p0-0f954158d_720-{self.event}-combined_PEDataRelease.hdf5"
    @property
    def basename_raw(self) -> str:
        return self.basename_h5
    @property
    def basename(self) -> str:
        return self.basename_h5
    @property
    def waveform_group(self) -> str:
        return '.'

    # Dataset address
    def dset_addr(self, wav) -> str:
        if wav not in self.waveforms:
            raise ValueError(f"waveform {wav} not in waveforms: {self.waveforms}")
        addr = None
        for key in WAVEFORM_ALIAS:
            if not WAVEFORM_ALIAS[key] == wav:
                continue
            if self.db.exists(path.join(key,'posterior_samples'),kind='dset'):
                addr = path.join(key,"posterior_samples")
        if addr is None:
            self.db.scan()
            raise RuntimeError(f"{__class__.dset_addr} is not defined correctly")
        if not self.db.exists(addr,kind='dset'):
            db.list_items(wav)
            raise RuntimeError(f"{__class__.dset_addr} is not defined correctly")
        return addr
    @property
    def url(self) -> str:
        return f"https://zenodo.org/records/16053484/files/IGWN-GWTC4p0-0f954158d_720-{self.event}-combined_PEDataRelease.hdf5"


class NRSurCat_1_EventCatalog(EventCatalog):
    """https://zenodo.org/records/8115310"""
    events = EVENTS["NRSurCat-1"]
    @property
    def catalog(self) -> str:
        return "NRSurCat-1"
    @property
    def basename_h5(self) -> str:
        return f"{self.event}_NRSur7dq4.h5"
    @property
    def basename_raw(self) -> str:
        return self.basename_h5
    @property
    def basename(self) -> str:
        return self.basename_h5
    @property
    def waveform_group(self) -> str:
        return '.'

    # Dataset address
    def dset_addr(self, wav) -> str:
        if wav not in self.waveforms:
            raise ValueError(f"waveform {wav} not in waveforms: {self.waveforms}")
        addr = None
        for key in WAVEFORM_ALIAS:
            if not WAVEFORM_ALIAS[key] == wav:
                continue
            if self.db.exists(path.join(key,'posterior_samples'),kind='dset'):
                addr = path.join(key,"posterior_samples")
        if addr is None:
            self.db.scan()
            raise RuntimeError(f"{__class__.dset_addr} is not defined correctly")
        if not self.db.exists(addr,kind='dset'):
            db.list_items(wav)
            raise RuntimeError(f"{__class__.dset_addr} is not defined correctly")
        return addr
    @property
    def url(self) -> str:
        return f"https://zenodo.org/records/8115310/files/{self.event}_NRSur7dq4.h5"

class Local_EventCatalog(EventCatalog):
    """From files"""
    def __init__(
            self, 
            event, 
            fname, 
            catalog_label,
            wav_group='.',
        ):
        """Initialize a local filesystem catalog object for a given event

        Inputs
        ------
        event : str
            Phone number for event (GW231123)
        fname : str
            Path to file on local machine
        catalog_label : str
            Name of this catalog
        wav_group : str
            Waveform group
        """
        self.event = event
        if not path.isfile(fname):
            raise ValueError(f"No such file: {fname}")
        self._catalog = catalog_label
        self._fname = fname
        self._wav_group = wav_group
        self.registry = Registry()

    events = EVENTS["NRSurCat-1"]
    @property
    def catalog(self) -> str:
        return self._catalog
    @property
    def catalog_events(self) -> list:
        return [self.event]
    @property
    def basename_h5(self) -> str:
        return path.basename(self._fname)
    @property
    def basename_raw(self) -> str:
        return self.basename
    @property
    def basename(self) -> str:
        return self.basename_
    @property
    def waveform_group(self) -> str:
        return self._wav_group

    # Dataset address
    def dset_addr(self, wav) -> str:
        if wav not in self.waveforms:
            raise ValueError(f"waveform {wav} not in waveforms: {self.waveforms}")
        addr = None
        for key in WAVEFORM_ALIAS:
            if not WAVEFORM_ALIAS[key] == wav:
                continue
            if self.db.exists(path.join(key,'posterior_samples'),kind='dset'):
                addr = path.join(key,"posterior_samples")
        if addr is None:
            self.db.scan()
            raise RuntimeError(f"{__class__.dset_addr} is not defined correctly")
        if not self.db.exists(addr,kind='dset'):
            db.list_items(wav)
            raise RuntimeError(f"{__class__.dset_addr} is not defined correctly")
        return addr
    @property
    def url(self) -> str:
        return self._fname
    @property
    def fname(self) ->str:
        return self._fname

CATALOGS = {
    "GWTC-1" : GWTC_1_EventCatalog,
    "GWTC-2" : GWTC_2_EventCatalog,
    "GWTC-2p1" : GWTC_2p1_EventCatalog,
    "GWTC-3" : GWTC_3_EventCatalog,
    "GWTC-4" : GWTC_4_EventCatalog,
    "NRSurCat-1" : NRSurCat_1_EventCatalog,
}
