menuText = [["DEVELOP",
            ["Color C-41", "Color E-6", "B&W", "Back"],
            ["Setup", "Back"],
            ["Over/Under Develop", "Agitation"]],
            ["SETTINGS",
            ["Sound", "Language", "Back"]],
            ["TEST",
            ["Test Stepper", "Back"]]]

# LIDI = List Dictionary.  There is definitely a better way to do this.
menuLidi = [
    ["DEVELOP",
        [
            ["Color", 
                {
                    "Developer": ["C-41", "E-6", "ECN-2", "Other", "Back"],
                    "Agitation": ["Normal", "Constant", "Custom Interval", "Back"],
                    "Push/Pull": ["Normal", "Push 1", "Push 2", "Push 3", "Pull 1", "Custom", "Back"],                    
                }
            ],
            ["B&W",
                {
                    "Developer": ["C-76", "HC", "Rodinal", "Other", "Back"],
                    "Film Stock": ["T-Max 400", "Tri-X 400", "HP-5", "Fomapan 400", "T-Max 3200"],
                }
            ],            
            ["Manual",
                {
                    "modes": ["Setup", "Back"],
                }
            ],
            ["User Preset",
                {
                    "modes": ["Browse", "Back"],
                }
            ],
        ]
    ]
]

tempTimes = {   "Normal": 
                {
                    22.0 : 50.00,
                    24.0 : 35.00,
                    27.0 : 21.00,
                    29.5 : 13.00,
                    32.0 : 8.50,
                    35.0 : 5.75,
                    39.0 : 3.50,
                },
                "Push 1" :
                {                    
                    24.0 : 50.00,
                    27.0 : 28.00,
                    29.5 : 17.00,
                    32.0 : 11.00,
                    35.0 : 7.50,
                    39.0 : 4.55,
                },
                "Push 2" :
                {                    
                    27.0 : 37.00,
                    29.5 : 25.00,
                    32.0 : 14.75,
                    35.0 : 10.00,
                    39.0 : 6.73,
                },
                "Push 3" :
                {                    
                    29.5 : 35.00,
                    32.0 : 21.00,
                    35.0 : 14.33,
                    39.0 : 8.75,
                },
                "Pull 1" :
                {                    
                    24.0 : 27.00,
                    27.0 : 16.25,
                    29.5 : 10.00,
                    32.0 : 6.50,
                    35.0 : 4.50,
                    39.0 : 2.75,
                },
            }