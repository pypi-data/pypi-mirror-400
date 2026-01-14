from BetterConfigAJM.BetterConfigAJM import BetterConfigAJM as BetterConfig


class UCWrapBetterConfig(BetterConfig):
    def __init__(self, config_filename, config_dir, config_list_dict=None):
        # noinspection SpellCheckingInspection
        super().__init__(config_filename, config_dir)
        self.default_config = [
            {'DEFAULT':
                 {
                     "user_email_suffix": "@albanyny.gov",
                     "base_url": "https://api.ucld.us/env/prd/"
                  },
             'AUTH':
                 {"user": "",
                  "password": "",
                  "auth_runtype_default": "read",
                  "key_dirpath": "../Misc_Project_Files"
                  }
             }
        ]

        if config_list_dict:
            self.config_list_dict = config_list_dict
        else:
            self.config_list_dict = self.default_config
