
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import java.lang
import jneqsim.neqsim.thermo.system
import jneqsim.neqsim.thermo.util.Vega
import jneqsim.neqsim.thermo.util.benchmark
import jneqsim.neqsim.thermo.util.constants
import jneqsim.neqsim.thermo.util.derivatives
import jneqsim.neqsim.thermo.util.empiric
import jneqsim.neqsim.thermo.util.gerg
import jneqsim.neqsim.thermo.util.humidair
import jneqsim.neqsim.thermo.util.jni
import jneqsim.neqsim.thermo.util.leachman
import jneqsim.neqsim.thermo.util.readwrite
import jneqsim.neqsim.thermo.util.referenceequations
import jneqsim.neqsim.thermo.util.spanwagner
import jneqsim.neqsim.thermo.util.steam
import typing



class FluidClassifier:
    @staticmethod
    def calculateC7PlusContent(systemInterface: jneqsim.neqsim.thermo.system.SystemInterface) -> float: ...
    @staticmethod
    def classify(systemInterface: jneqsim.neqsim.thermo.system.SystemInterface) -> 'ReservoirFluidType': ...
    @staticmethod
    def classifyByC7Plus(double: float) -> 'ReservoirFluidType': ...
    @staticmethod
    def classifyByGOR(double: float) -> 'ReservoirFluidType': ...
    @staticmethod
    def classifyWithPhaseEnvelope(systemInterface: jneqsim.neqsim.thermo.system.SystemInterface, double: float) -> 'ReservoirFluidType': ...
    @staticmethod
    def estimateAPIGravity(systemInterface: jneqsim.neqsim.thermo.system.SystemInterface) -> float: ...
    @staticmethod
    def generateClassificationReport(systemInterface: jneqsim.neqsim.thermo.system.SystemInterface) -> java.lang.String: ...

class ReservoirFluidType(java.lang.Enum['ReservoirFluidType']):
    DRY_GAS: typing.ClassVar['ReservoirFluidType'] = ...
    WET_GAS: typing.ClassVar['ReservoirFluidType'] = ...
    GAS_CONDENSATE: typing.ClassVar['ReservoirFluidType'] = ...
    VOLATILE_OIL: typing.ClassVar['ReservoirFluidType'] = ...
    BLACK_OIL: typing.ClassVar['ReservoirFluidType'] = ...
    HEAVY_OIL: typing.ClassVar['ReservoirFluidType'] = ...
    UNKNOWN: typing.ClassVar['ReservoirFluidType'] = ...
    def getDisplayName(self) -> java.lang.String: ...
    def getTypicalC7PlusRange(self) -> java.lang.String: ...
    def getTypicalGORRange(self) -> java.lang.String: ...
    def toString(self) -> java.lang.String: ...
    _valueOf_0__T = typing.TypeVar('_valueOf_0__T', bound=java.lang.Enum)  # <T>
    @typing.overload
    @staticmethod
    def valueOf(class_: typing.Type[_valueOf_0__T], string: typing.Union[java.lang.String, str]) -> _valueOf_0__T: ...
    @typing.overload
    @staticmethod
    def valueOf(string: typing.Union[java.lang.String, str]) -> 'ReservoirFluidType': ...
    @staticmethod
    def values() -> typing.MutableSequence['ReservoirFluidType']: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.thermo.util")``.

    FluidClassifier: typing.Type[FluidClassifier]
    ReservoirFluidType: typing.Type[ReservoirFluidType]
    Vega: jneqsim.neqsim.thermo.util.Vega.__module_protocol__
    benchmark: jneqsim.neqsim.thermo.util.benchmark.__module_protocol__
    constants: jneqsim.neqsim.thermo.util.constants.__module_protocol__
    derivatives: jneqsim.neqsim.thermo.util.derivatives.__module_protocol__
    empiric: jneqsim.neqsim.thermo.util.empiric.__module_protocol__
    gerg: jneqsim.neqsim.thermo.util.gerg.__module_protocol__
    humidair: jneqsim.neqsim.thermo.util.humidair.__module_protocol__
    jni: jneqsim.neqsim.thermo.util.jni.__module_protocol__
    leachman: jneqsim.neqsim.thermo.util.leachman.__module_protocol__
    readwrite: jneqsim.neqsim.thermo.util.readwrite.__module_protocol__
    referenceequations: jneqsim.neqsim.thermo.util.referenceequations.__module_protocol__
    spanwagner: jneqsim.neqsim.thermo.util.spanwagner.__module_protocol__
    steam: jneqsim.neqsim.thermo.util.steam.__module_protocol__
