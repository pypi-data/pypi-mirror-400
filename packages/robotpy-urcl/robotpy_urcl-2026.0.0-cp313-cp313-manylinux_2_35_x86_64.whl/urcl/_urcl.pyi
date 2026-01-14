from __future__ import annotations
import collections.abc
import typing
import wpiutil._wpiutil.log
__all__: list[str] = ['URCL']
class URCL:
    """
    URCL (Unofficial REV-Compatible Logger)
    
    This unofficial logger enables automatic capture of CAN traffic from REV
    motor controllers to NetworkTables, viewable using AdvantageScope. See the
    corresponding AdvantageScope documentation for more details:
    https://github.com/Mechanical-Advantage/AdvantageScope/blob/main/docs/REV-LOGGING.md
    
    As this library is not an official REV tool, support queries should be
    directed to the URCL issues page or software@team6328.org
    rather than REV's support contact.
    """
    @staticmethod
    @typing.overload
    def start() -> None:
        """
        Start capturing data from REV motor controllers to NetworkTables. This
        method should only be called once.
        """
    @staticmethod
    @typing.overload
    def start(log: wpiutil._wpiutil.log.DataLog) -> None:
        """
        Start capturing data from REV motor controllers to a DataLog. This method
        should only be called once.
        
        :param log: The DataLog object to log to.
        """
    @staticmethod
    @typing.overload
    def start(aliases: collections.abc.Mapping[typing.SupportsInt, str]) -> None:
        """
        Start capturing data from REV motor controllers to NetworkTables. This
        method should only be called once.
        
        :param aliases: The set of aliases mapping CAN IDs to names.
        """
    @staticmethod
    @typing.overload
    def start(aliases: collections.abc.Mapping[typing.SupportsInt, str], log: wpiutil._wpiutil.log.DataLog) -> None:
        """
        Start capturing data from REV motor controllers to a DataLog. This method
        should only be called once.
        
        :param aliases: The set of aliases mapping CAN IDs to names.
        :param withNT:  Whether or not to run with NetworkTables.
        """
