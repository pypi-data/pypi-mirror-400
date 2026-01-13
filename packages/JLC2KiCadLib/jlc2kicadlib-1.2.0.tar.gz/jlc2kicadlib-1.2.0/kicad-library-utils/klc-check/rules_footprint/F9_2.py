from rules_footprint.rule import KLCRule


class Rule(KLCRule):
    """Footprint properties should be left to default values"""

    def check(self) -> bool:
        """
        Proceeds the checking of the rule.
        """

        module = self.module

        err = False

        if module.locked:
            self.error("Module is locked!")
            err = True
        if module.autoplace_cost90 != 0:
            self.warning(
                f"Attribute autoplace_cost90 == {module.autoplace_cost90} != 0!"
            )
        if module.autoplace_cost180 != 0:
            self.warning(
                f"Attribute autoplace_cost180 == {module.autoplace_cost180} != 0!"
            )

        # Following is allowed (with warning) to conform to manufacturer specifications
        if module.clearance != 0:
            self.warning(f"Attribute clearance == {module.clearance} != 0!")
        if module.solder_mask_margin != 0:
            self.warning(
                f"Attribute solder_mask_margin == {module.solder_mask_margin} != 0!"
            )
        if module.solder_paste_margin != 0:
            self.warning(
                f"Attribute solder_paste_margin == {module.solder_paste_margin} != 0!"
            )
        if module.solder_paste_ratio != 0:
            self.warning(
                f"Attribute solder_paste_ratio == {module.solder_paste_ratio} != 0!"
            )

        return err

    def fix(self) -> None:
        """
        Proceeds the fixing of the rule, if possible.
        """

        module = self.module
        if self.check():
            self.info("Setting footprint properties to default values")
            module.locked = False
            module.autoplace_cost90 = 0
            module.autoplace_cost180 = 0

            # These might actually be required to match datasheet spec.

            # module.clearance = 0
            # module.solder_mask_margin = 0
            # module.solder_paste_margin = 0
            # module.solder_paste_ratio = 0
