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
                    # [["AGITATION"],
                    # ["NORM", "CNST"]],
                    [["PUSH/PULL"],
                    ["-1","0","+1","+2","+3"]],
                    [["ROLLS DEVED"],
                    [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]],
                    [["START"], ["","CONFIRM"]],    
                    [["BACK"], ["",""]]                  
                ]],
                [["DEVELOP B&W"], 
                [
                    [["DEVELOPER"],
                    ["C-76", "HC", "RDNL", "Other"]],
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