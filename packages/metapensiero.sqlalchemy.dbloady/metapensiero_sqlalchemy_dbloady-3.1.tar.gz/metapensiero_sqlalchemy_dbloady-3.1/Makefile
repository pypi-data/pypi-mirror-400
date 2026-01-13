# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady —
# :Created:   dom 4 giu 2023, 17:38:28
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2023, 2024, 2026 Lele Gaifax
#

# List of Python versions to test against, keep it in sync with flake.nix
SNAKES = 313 314

.PHONY: test

define test-snake
test:: test-python$(1)

.PHONY: test-python$(1)
test-python$(1):
	nix develop '.#test-python$(1)' -c just check
endef

$(foreach snake,$(SNAKES),$(eval $(call test-snake,$(snake))))
