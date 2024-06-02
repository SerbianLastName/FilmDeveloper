menuText = [["DEVELOP",
            ["Color C-41", "Color E-6", "B&W", "Back"],
            ["Setup", "Back"],
            ["Over/Under Develop", "Agitation"]],
            ["SETTINGS",
            ["Sound", "Language", "Back"]],
            ["TEST",
            ["Test Stepper", "Back"]]]

# I feel like, maybe, a dictionary would be better here, but whatever.
menus =   [["DEVELOP",
                [
                [["DEVELOP COLOR"], 
                [
                    [["DEVELOPER"],
                    ["C-41", "E-6", "ECN2"]],
                    [["AGITATION"],
                    ["NORM", "CNST"]],
                    [["PUSH/PULL"],
                    ["-1","0","+1","+2","+3"]],
                    [["START"], ["","CONFIRM"]],    
                    [["BACK"], ["",""]]                  
                ]],
                [["DEVELOP B&W"], 
                [
                    [["DEVELOPER"],
                    ["C-76", "HC", "Rodinal", "Other"]],
                    [["FILM"],
                    ["T-MAX 400", "TRI-X 400", "HP-5", "FOMA 400", "T-MAX 3200"]],
                    [["Push/Pull"],
                    ["-1","0","+1","+2","+3"]],
                    [["AGITATION"],
                    ["NORM", "CNST"]],                    
                    [["START"], ["","CONFIRM"]],                     
                    [["BACK"], ["",""]],                       
                ]],
                [["BACK"], 
                [
                    [["BACK"],
                    ["",""]]                      
                ]],
                ],
            ],
            ["DEVELOP 2",
                [
                [["DEVELOP COLOR"], 
                [
                    [["Developer"],
                    ["C-41", "E-6", "ECN-2", "Other"]],
                    [["Agitation"],
                    ["Normal", "Constant", "Custom Interval"]],
                    [["Push/Pull"],
                    [-1,0,+1,+2,+3]],
                    [["BACK"], [""]]                    
                ]],
                [["DEVELOP B&W"], 
                [
                    [["Developer"],
                    ["T-Max 400", "Tri-X 400", "HP-5", "Fomapan 400", "T-Max 3200"]],
                    [["Agitation"],
                    ["Normal", "Constant", "Custom Interval",]],
                    [["Push/Pull"],
                    [-1,0,1,2,3]],
                    [["BACK"], [""]]                       
                ]],
                [["BACK"], 
                [
                    [["BACK"],
                    [""]]                      
                ]],
                ],
            ],         
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