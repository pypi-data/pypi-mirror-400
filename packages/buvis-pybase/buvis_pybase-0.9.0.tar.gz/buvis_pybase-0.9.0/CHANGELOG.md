# CHANGELOG

<!-- version list -->

## v0.9.0 (2026-01-07)


## v0.8.1 (2026-01-04)


## v0.8.0 (2026-01-04)

### Bug Fixes

- **adapters**: Type hints, return types, error logging, autodoc members
  ([`2e65409`](https://github.com/buvis/buvis-pybase/commit/2e6540975dec648d1a6d06c39c2de5a98a3575d1))

- **jira**: Add None default to os.environ.pop() for proxy vars
  ([`a0e1b8d`](https://github.com/buvis/buvis-pybase/commit/a0e1b8d658e03bba29a9f309270dc6820498003b))

- **outlook**: Correct date format from %Y-%d-%m to %Y-%m-%d
  ([`7cc4263`](https://github.com/buvis/buvis-pybase/commit/7cc42638991fa91f784542ad83d042b893321d7d))

- **shell**: Correct ShellAdapter.exe return type from None to tuple[str, str]
  ([`f5ade04`](https://github.com/buvis/buvis-pybase/commit/f5ade048de56e6c2847ef7399c414397b74718a8))

### Features

- Add _get_candidate_files for interleaved config file paths
  ([`b7210ac`](https://github.com/buvis/buvis-pybase/commit/b7210acd7707694830eacb312e529313357a7752))

- Add _get_candidate_files for interleaved config file paths
  ([`7d2a406`](https://github.com/buvis/buvis-pybase/commit/7d2a40604b1e794a97687f1a231e2108621c0010))

- Add _get_search_paths with 4-location priority order
  ([`4add8d4`](https://github.com/buvis/buvis-pybase/commit/4add8d4fa92db239e687430b4040052123c86c80))

- Add _get_search_paths with 4-location priority order
  ([`3b729ca`](https://github.com/buvis/buvis-pybase/commit/3b729ca5080fc8be7bd3f0b1630edd2ee94c5def))

- Add _load_yaml_config function to resolver
  ([`42fea03`](https://github.com/buvis/buvis-pybase/commit/42fea032329f99dd8714985a7da6e153912ac34e))

- Add _load_yaml_config function to resolver
  ([`1a0384b`](https://github.com/buvis/buvis-pybase/commit/1a0384b1c1c91990ab7ee9cba5a531674cd13f43))

- Add _substitute function for env var substitution
  ([`d5e94aa`](https://github.com/buvis/buvis-pybase/commit/d5e94aa62c3dba3c56f452f7bec32e839f60e9ab))

- Add _substitute function for env var substitution
  ([`a9c0940`](https://github.com/buvis/buvis-pybase/commit/a9c0940e3cfeef2cfa03e8a30d1df8782ad79a73))

- Add buvis_options Click decorator for CLI integration
  ([`e55e976`](https://github.com/buvis/buvis-pybase/commit/e55e976c43e48c92e7e73503b1a042bb7462a2d2))

- Add buvis_options Click decorator for CLI integration
  ([`c48664f`](https://github.com/buvis/buvis-pybase/commit/c48664f85bff39a80423cce066cb8f8203a26685))

- Add BuvisSettings base class with BUVIS_ env prefix
  ([`b90a374`](https://github.com/buvis/buvis-pybase/commit/b90a374e474a2fd9092f0d0d4df6796519d89850))

- Add BuvisSettings base class with BUVIS_ env prefix
  ([`c3834cc`](https://github.com/buvis/buvis-pybase/commit/c3834cc1e6472c81eff51b5b5c4db69febee84f2))

- Add ConfigResolver for settings resolution with CLI overrides
  ([`d306adc`](https://github.com/buvis/buvis-pybase/commit/d306adc58adcfd85c38a5114797a5adcdf3a6c6b))

- Add ConfigResolver for settings resolution with CLI overrides
  ([`48885ef`](https://github.com/buvis/buvis-pybase/commit/48885eff3ed72de5b7a675441223b99948cd148a))

- Add ConfigResolver precedence logic (CLI > ENV > YAML > Defaults)
  ([`28124ca`](https://github.com/buvis/buvis-pybase/commit/28124ca12add7e3b965cc541bcc98321eea7e712))

- Add ConfigResolver precedence logic (CLI > ENV > YAML > Defaults)
  ([`a882b5a`](https://github.com/buvis/buvis-pybase/commit/a882b5aea1caf5269d3b9dbe0d8f657ed8208022))

- Add ConfigurationError with enhanced YAML error handling
  ([`e5107a0`](https://github.com/buvis/buvis-pybase/commit/e5107a09750a44e3d92f5fbb51f3fc619c6c4093))

- Add ConfigurationError with enhanced YAML error handling
  ([`8f40d72`](https://github.com/buvis/buvis-pybase/commit/8f40d7251196d9dd4e6503ef61ee8d54720085c9))

- Add ConfigurationLoader class scaffold with find_config_files stub
  ([`d2901be`](https://github.com/buvis/buvis-pybase/commit/d2901beafc42885879160facce35828b8b90981f))

- Add ConfigurationLoader class scaffold with find_config_files stub
  ([`5050a21`](https://github.com/buvis/buvis-pybase/commit/5050a210dc46f65c36c1e73a8b6ba04d728dd501))

- Add create_tool_settings_class factory for tool-specific settings
  ([`b83c512`](https://github.com/buvis/buvis-pybase/commit/b83c512d100432a60794c8eb48678a50e541ec28))

- Add create_tool_settings_class factory for tool-specific settings
  ([`ef1ef8c`](https://github.com/buvis/buvis-pybase/commit/ef1ef8c8371693db6678c6acf2fd164ffc181380))

- Add deep merge functionality for config dicts
  ([`ae11575`](https://github.com/buvis/buvis-pybase/commit/ae115755971a393597a7eb7af6cfc935e989dea9))

- Add deep merge functionality for config dicts
  ([`a19d96c`](https://github.com/buvis/buvis-pybase/commit/a19d96c46a7b6b5f0e96e9d7539f9161e1469689))

- Add env var name validator for BUVIS convention
  ([`c6284d0`](https://github.com/buvis/buvis-pybase/commit/c6284d04e2604273f764aaa853e60de4ebec8275))

- Add env var name validator for BUVIS convention
  ([`38fa58e`](https://github.com/buvis/buvis-pybase/commit/38fa58e2149db609235f8ce87d1c419d6ced4012))

- Add env var pattern regex to ConfigurationLoader
  ([`1718511`](https://github.com/buvis/buvis-pybase/commit/1718511db06540590c5f271b4f5028a50b91cb0b))

- Add env var pattern regex to ConfigurationLoader
  ([`96a6471`](https://github.com/buvis/buvis-pybase/commit/96a64715d5b27c241c8c6467c45de4e699aece13))

- Add escape syntax for literal ${VAR} in config files
  ([`a5e4fde`](https://github.com/buvis/buvis-pybase/commit/a5e4fdefc0392be345daae5dcfc1d9b70067479c))

- Add escape syntax for literal ${VAR} in config files
  ([`c4c62a4`](https://github.com/buvis/buvis-pybase/commit/c4c62a45b5081323417f673062c1176e0f964f00))

- Add get_settings helper for Click context retrieval
  ([`8bef2c2`](https://github.com/buvis/buvis-pybase/commit/8bef2c27b098580daffd7cfd553f2ac15e139cce))

- Add get_settings helper for Click context retrieval
  ([`e5e5af4`](https://github.com/buvis/buvis-pybase/commit/e5e5af40899d1f8fee989025afa6d0aa62c7d909))

- Add GlobalSettings with BUVIS_ env prefix and validation
  ([`5554c7b`](https://github.com/buvis/buvis-pybase/commit/5554c7ba82efbe2e3a8ec493a8840b64d2e32c0b))

- Add GlobalSettings with BUVIS_ env prefix and validation
  ([`9924bc4`](https://github.com/buvis/buvis-pybase/commit/9924bc4822f094da70a821ad307eef17a96802bc))

- Add HCMSettings with dict[str, str] headers field
  ([`f3d553a`](https://github.com/buvis/buvis-pybase/commit/f3d553a20c147c0a63431bdf9a43d2e21c07155b))

- Add HCMSettings with dict[str, str] headers field
  ([`01aa56d`](https://github.com/buvis/buvis-pybase/commit/01aa56dd899197ec0102cbed75ccc1295f879845))

- Add idle_timeout to PoolSettings and test mixed underscore parsing
  ([`567fe5c`](https://github.com/buvis/buvis-pybase/commit/567fe5ca61f1d54e63ef311e7ff01926cca21b0b))

- Add idle_timeout to PoolSettings and test mixed underscore parsing
  ([`e51c1fd`](https://github.com/buvis/buvis-pybase/commit/e51c1fd1d0034e1ea73cfbde90650475f9bcd5c8))

- Add JSON env size limit validator (64KB max)
  ([`e51daef`](https://github.com/buvis/buvis-pybase/commit/e51daefbf8873bdaaaab1fef9c724064293c53e5))

- Add JSON env size limit validator (64KB max)
  ([`252a31e`](https://github.com/buvis/buvis-pybase/commit/252a31eccf237c9111b6bbaca2851f5c30b92b46))

- Add load_yaml method with env var substitution
  ([`e192dad`](https://github.com/buvis/buvis-pybase/commit/e192dadada8d4cdea25b2b9e512fad7a5075b8a3))

- Add load_yaml method with env var substitution
  ([`f76723a`](https://github.com/buvis/buvis-pybase/commit/f76723ae93a91f8ec12a8ec6611f792a33c36605))

- Add MissingEnvVarError for clearer env var error handling
  ([`9468811`](https://github.com/buvis/buvis-pybase/commit/946881109d3c5970b22d5c36131a3b49b00fd824))

- Add MissingEnvVarError for clearer env var error handling
  ([`150eba2`](https://github.com/buvis/buvis-pybase/commit/150eba2209850dd2d8a6f1814336868a359572ac))

- Add nested settings examples with __ delimiter pattern
  ([`7d1261b`](https://github.com/buvis/buvis-pybase/commit/7d1261ba3212e9ab28b3d34f831ad66d941d614b))

- Add nested settings examples with __ delimiter pattern
  ([`72b3ea0`](https://github.com/buvis/buvis-pybase/commit/72b3ea09075b52b525c5ba029307b1e1dc9f5add))

- Add nesting depth validator for settings models
  ([`b8a2173`](https://github.com/buvis/buvis-pybase/commit/b8a21734ad724061ebd2fca76637b0b2c224ddce))

- Add nesting depth validator for settings models
  ([`bb69c36`](https://github.com/buvis/buvis-pybase/commit/bb69c36911905818ddea2856360383a58fd8e6c0))

- Add optional env var substitution to Configuration class
  ([`bd9f5c0`](https://github.com/buvis/buvis-pybase/commit/bd9f5c0b885b4aecc928c40bfea8d7c4dd718060))

- Add optional env var substitution to Configuration class
  ([`e5c73c6`](https://github.com/buvis/buvis-pybase/commit/e5c73c692f7173d333a6ff9df82e9087fcfe5eb8))

- Add PaymentRule model for JSON array env var parsing
  ([`590669f`](https://github.com/buvis/buvis-pybase/commit/590669f5c6f12d7ac789bd59c832dc5f4df20e81))

- Add PaymentRule model for JSON array env var parsing
  ([`8487256`](https://github.com/buvis/buvis-pybase/commit/848725624b69f5851fb56c4c4e412c7dca4bfcc4))

- Add SafeLoggingMixin for sensitive value masking
  ([`52820b3`](https://github.com/buvis/buvis-pybase/commit/52820b318cafe8720d59d516ff19414cb9d5f10f))

- Add SafeLoggingMixin for sensitive value masking
  ([`4ff488c`](https://github.com/buvis/buvis-pybase/commit/4ff488c434af5bbd1859413faf3103e3afd72248))

- Add secret masking in validation error messages
  ([`c2df271`](https://github.com/buvis/buvis-pybase/commit/c2df271ec6632b8ce295a13c49623222b11d8314))

- Add secret masking in validation error messages
  ([`a07312a`](https://github.com/buvis/buvis-pybase/commit/a07312a93679f19a93f30945fa03227c00712f33))

- Add SecureSettingsMixin for JSON size validation
  ([`3a1fcf8`](https://github.com/buvis/buvis-pybase/commit/3a1fcf8821d99dd3a938bc0f67e51cb3da77844b))

- Add SecureSettingsMixin for JSON size validation
  ([`12af7c1`](https://github.com/buvis/buvis-pybase/commit/12af7c1933a4d45218b6263506a80d3f7c8ed058))

- Add source tracking and DEBUG logging to ConfigResolver
  ([`7288e42`](https://github.com/buvis/buvis-pybase/commit/7288e42c4c51dfdcc81686dca66bf33200084b14))

- Add source tracking and DEBUG logging to ConfigResolver
  ([`ff433cd`](https://github.com/buvis/buvis-pybase/commit/ff433cd8f3535ecc230b71869db788404c2fa077))

- Add symlink security validation to DirTree traversal
  ([`9476be8`](https://github.com/buvis/buvis-pybase/commit/9476be88a97e78ee243724c8ebe12eb0e8426219))

- Add symlink security validation to DirTree traversal
  ([`2135f30`](https://github.com/buvis/buvis-pybase/commit/2135f305fc47b8ddc6b7a95c1d572fa4a41c93ff))

- Add tool_name validation (lowercase, no hyphens)
  ([`ee5044c`](https://github.com/buvis/buvis-pybase/commit/ee5044cfeeb9b593ed8cbe301848488127041ec5))

- Add tool_name validation (lowercase, no hyphens)
  ([`3799bce`](https://github.com/buvis/buvis-pybase/commit/3799bcec0e32a1bba253cfec84ed014fa6375478))

- Add ToolSettings base model with frozen and extra=forbid
  ([`fffd2b2`](https://github.com/buvis/buvis-pybase/commit/fffd2b2f324617d92aed20e9c5b4a2fc88c7d435))

- Add ToolSettings base model with frozen and extra=forbid
  ([`1050c4f`](https://github.com/buvis/buvis-pybase/commit/1050c4f9172fa2993bb3bd3ddbd44f6f15ac526b))

- Add try/finally for config_dir env var restoration
  ([`b36fdbc`](https://github.com/buvis/buvis-pybase/commit/b36fdbcd68d01abd5ffaa22e2f08f797bc504429))

- Add try/finally for config_dir env var restoration
  ([`e4b1833`](https://github.com/buvis/buvis-pybase/commit/e4b1833257dcf135195df855675ea121b793e34c))

- Add world-writable config file detection with warning
  ([`b153c4f`](https://github.com/buvis/buvis-pybase/commit/b153c4f2407975a5dd7067ccde185e997e5b1ff6))

- Add world-writable config file detection with warning
  ([`a38d9a2`](https://github.com/buvis/buvis-pybase/commit/a38d9a228b3f052e21649ac0c550b16d731b933f))

- Implement find_config_files with security validation
  ([`986b059`](https://github.com/buvis/buvis-pybase/commit/986b0590e3f3ac039d95c5636d039992d4ce47e9))

- Implement find_config_files with security validation
  ([`1147cb4`](https://github.com/buvis/buvis-pybase/commit/1147cb4c3ce8d96e75f66251683916eecaa7ea0a))

- Integrate ConfigurationLoader with Configuration class
  ([`fdb41ca`](https://github.com/buvis/buvis-pybase/commit/fdb41caf482b58448d78ce8500ea3907401aa1ed))

- Integrate ConfigurationLoader with Configuration class
  ([`e9dc253`](https://github.com/buvis/buvis-pybase/commit/e9dc2536daae49751feae5755833854e8eadceed))

- Log sensitive config fields at INFO level
  ([`4078118`](https://github.com/buvis/buvis-pybase/commit/407811829b12f7695e6789b60194ce808c708c96))

- Log sensitive config fields at INFO level
  ([`879e0ba`](https://github.com/buvis/buvis-pybase/commit/879e0ba05bd9dddb9c503b49fdccf67bbf5320e2))

- Wrap ValidationError in ConfigurationError with field paths
  ([`f2c6476`](https://github.com/buvis/buvis-pybase/commit/f2c6476c3e0f172b1599a3b02bf5fc7ea86283ad))

- Wrap ValidationError in ConfigurationError with field paths
  ([`1e50417`](https://github.com/buvis/buvis-pybase/commit/1e504174977c28d38116fe84136ec959254c9a27))

- **click**: Add type-safe get_settings with settings_class parameter
  ([`e4192c0`](https://github.com/buvis/buvis-pybase/commit/e4192c05470205be7181acaf477ab75dcd9ed7d3))

- **click**: Parameterize buvis_options with settings_class for tool-specific settings
  ([`64c9d7e`](https://github.com/buvis/buvis-pybase/commit/64c9d7e0a79b225c07e58302c30e29d17f644d5f))

- **configuration**: Centralize defaults of configuration items
  ([#13](https://github.com/buvis/buvis-pybase/pull/13),
  [`98c5a62`](https://github.com/buvis/buvis-pybase/commit/98c5a624fae671c1d77d78944736a5918bee31e5))

- **configuration**: Remove legacy cfg singleton
  ([`f21f4b5`](https://github.com/buvis/buvis-pybase/commit/f21f4b5cd5b131a08e077aa34d665e3243cd4da7))

- **configuration**: Remove legacy cfg singleton
  ([`90c05c1`](https://github.com/buvis/buvis-pybase/commit/90c05c159284451613464393ca38cde2751f238c))

- **examples**: Add PhotoSettings and MusicSettings example classes
  ([`6fe2d6e`](https://github.com/buvis/buvis-pybase/commit/6fe2d6e1cb11de2345370c3b7a2046f484c41f48))

- **resolver**: Add _extract_tool_name helper for env_prefix parsing
  ([`83d44de`](https://github.com/buvis/buvis-pybase/commit/83d44de09b12b80c385f8efa57953dfdc1add929))

- **resolver**: Derive tool_name from env_prefix and use config discovery
  ([`ae6cd50`](https://github.com/buvis/buvis-pybase/commit/ae6cd502587889407d63f63c999c567099079f91))


## v0.7.3 (2025-12-30)

### Bug Fixes

- Infinite loop when testing in development directory
  ([`47658a2`](https://github.com/buvis/buvis-pybase/commit/47658a220057302673b54427b9787124ca0fff56))


## v0.7.2 (2025-12-30)

### Bug Fixes

- Clean cache only on fail
  ([`59eefc8`](https://github.com/buvis/buvis-pybase/commit/59eefc890b7e5cc5ae2a813ff6f13cd9fe7b647b))


## v0.7.1 (2025-12-30)

### Features

- Clean cache before install
  ([`50af7c1`](https://github.com/buvis/buvis-pybase/commit/50af7c1165f1665ac2b34c492466b52fcb0c2124))


## v0.7.0 (2025-12-30)

### Features

- Add script execution logic
  ([`9654f65`](https://github.com/buvis/buvis-pybase/commit/9654f655712fab5399ee98c3377424eb21b2ec3a))


## v0.6.0 (2025-12-29)

### Bug Fixes

- Add missing __init__
  ([`7bbead1`](https://github.com/buvis/buvis-pybase/commit/7bbead1a4a48a01d300fc6d126d5a5f6dcf939f1))

- Add upper bounds to all deps
  ([`288f879`](https://github.com/buvis/buvis-pybase/commit/288f879f8c49f11e87c285e862e3cecba942031b))

- Renovate+uv library compliance
  ([`7cb353b`](https://github.com/buvis/buvis-pybase/commit/7cb353bb01176a2551b278ddac3dd8440769bb36))

- Use only uv tool dir for individual projects/scripts
  ([`64aa6b5`](https://github.com/buvis/buvis-pybase/commit/64aa6b56f81252236ac7798d2706270835b11368))


## v0.5.7 (2025-12-23)

### Bug Fixes

- Typo in TextIOWrapper
  ([`da9ff96`](https://github.com/buvis/buvis-pybase/commit/da9ff963668e2e66613b4d055c2cb6ddbfe48f52))


## v0.5.6 (2025-12-23)

### Bug Fixes

- Windows unicode error in console (wrapping approach)
  ([`bc65096`](https://github.com/buvis/buvis-pybase/commit/bc65096d85a259a887362425e5d8c7463d6096bb))


## v0.5.5 (2025-12-23)

### Bug Fixes

- Windows unicode error in console
  ([`93e1d75`](https://github.com/buvis/buvis-pybase/commit/93e1d7594884e7f64c00ee890a466ea372c7f420))


## v0.5.4 (2025-12-23)

### Bug Fixes

- Upgrade tools where installed and not in src
  ([`cbebd88`](https://github.com/buvis/buvis-pybase/commit/cbebd8881135a439b8f92bba22a209470e3baec2))


## v0.5.3 (2025-12-23)

### Bug Fixes

- Deploy-docs use uv, trigger only on docs changes
  ([`10b2f20`](https://github.com/buvis/buvis-pybase/commit/10b2f203719dd7d07fb0aad957421d4c93fc8cfe))


## v0.3.0 (2025-12-22)


## v0.2.0 (2025-08-13)


## v0.1.8 (2025-08-13)


## v0.1.7 (2025-08-13)


## v0.1.5 (2025-08-13)


## v0.1.4 (2024-11-13)


## v0.1.3 (2024-09-08)


## v0.1.2 (2024-09-07)


## v0.1.1 (2024-09-07)


## v0.1.0 (2024-09-02)

- Initial Release
