from typing import List

from kicad_sym import KicadSymbol, Pin, mm_to_mil

from rules_symbol.rule import KLCRule, pinString


class Rule(KLCRule):
    """General pin requirements"""

    def __init__(self, component: KicadSymbol):
        super().__init__(component)

        self.violating_pins: List[Pin] = []

    def checkPinOrigin(self, gridspacing: int = 100) -> bool:
        self.violating_pins = []
        err = False
        for pin in self.component.pins:
            grid = gridspacing
            posx = mm_to_mil(pin.posx)
            posy = mm_to_mil(pin.posy)
            if pin.etype == "no_connect":
                # allow no_connect pins to be on a 50mil grid
                # when pinlength is 50 or 150mil, and they are on the outline, they will not be
                # on a 100mil grid.  we don't really care if they can easily be connected to, because
                # they are not supposed to be connected
                grid = 50
            if (posx % grid) != 0 or (posy % grid) != 0:
                self.violating_pins.append(pin)
                if not err:
                    self.error(
                        f"Pins not located on {grid}mil (={grid * 0.0254:.3}mm) grid:"
                    )
                self.error(f" - {pinString(pin, loc=True)} ")
                err = True

        return len(self.violating_pins) > 0

    def checkDuplicatePins(self) -> bool:
        test_pins = self.component.pins
        seen = set()
        for pin in test_pins:
            identity = (pin.number, pin.demorgan, pin.unit)
            if identity in seen:
                self.error(f"Pin {pin.number} is duplicated:")
                self.errorExtra(pinString(pin))
            seen.add(identity)

        return len(seen) != len(test_pins)  # true iff there are duplicates

    def checkPinLength(
        self, errorPinLength: int = 49, warningPinLength: int = 99
    ) -> bool:
        self.violating_pins = []

        for pin in self.component.pins:
            length = mm_to_mil(pin.length)

            err = False

            # ignore zero-length pins e.g. hidden power pins
            if length == 0:
                continue

            if length <= errorPinLength:
                self.error(
                    f"{pinString(pin)} length ({length}mils) is below {errorPinLength + 1}mils"
                )
            elif length <= warningPinLength:
                self.warning(
                    f"{pinString(pin)} length ({length}mils) is below {warningPinLength + 1}mils"
                )

            if length % 50 != 0:
                self.warning(
                    f"{pinString(pin)} length ({length}mils) is not a multiple of 50mils"
                )

            # length too long flags a warning
            if length > 300:
                err = True
                self.error(
                    f"{pinString(pin)} length ({length}mils) is longer than maximum (300mils)"
                )

            if err:
                self.violating_pins.append(pin)

        return len(self.violating_pins) > 0

    def check(self) -> bool:
        # no need to check pins on a derived symbols
        if self.component.extends is not None:
            return False

        # determine pin-grid:
        #  - standard components should use 100mil
        #  - "small" symbols (resistors, diodes, ...) should use 50mil
        pingrid = 100
        errorPinLength = 49
        warningPinLength = 99
        if self.component.is_small_component_heuristics():
            pingrid = 50
            errorPinLength = 24
            warningPinLength = 49

        return any(
            [
                self.checkPinOrigin(pingrid),
                self.checkPinLength(errorPinLength, warningPinLength),
                self.checkDuplicatePins(),
            ]
        )

    def fix(self) -> None:
        """
        Proceeds the fixing of the rule, if possible.
        """

        self.info("Fix not supported")

        if self.checkPinOrigin():
            pass

        if self.checkPinLength():
            pass
