# Compatibility

This table documents testing of the pymeu main functions (ex: get terminal info, download, upload, upload all, reboot).<br>
Some combinations have non-critical quirks or limitations.<br>

ME Version | PanelView Plus      | PanelView Plus 6  | PanelView Plus 7 Series A | PanelView Plus 7 Series B
-----------|---------------------|-------------------|---------------------------|----------------------------
v3.10      | Untested            | N/A               | N/A                       | N/A
v3.20      | Untested            | N/A               | N/A                       | N/A
v4.00      | Untested            | N/A               | N/A                       | N/A
v5.00      | Untested            | N/A               | N/A                       | N/A
v5.10      | Tested<sup>1,2</sup>| N/A               | N/A                       | N/A
v6.00      | N/A                 | Tested            | N/A                       | N/A
v6.10      | N/A                 | Tested            | N/A                       | N/A
v7.00      | N/A                 | Tested            | N/A                       | N/A
v8.00      | N/A                 | Tested            | Tested                    | N/A
v8.10      | N/A                 | Tested            | Tested                    | N/A
v8.20      | N/A                 | Tested            | Tested                    | N/A
v9.00      | N/A                 | Tested            | Tested                    | N/A
v10.00     | N/A                 | Tested            | Tested                    | N/A
v11.00     | N/A                 | Tested<sup>1</sup>| Tested                    | N/A
v12.00     | N/A                 | Tested            | Tested                    | Tested<sup>4</sup>
v13.00     | N/A                 | N/A               | Tested                    | Tested<sup>4</sup>
v14.00     | N/A                 | N/A               | Tested                    | Tested<sup>4</sup>
v15.00     | N/A                 | N/A               | Tested<sup>3</sup>        | Tested<sup>3,4</sup>

<sup>1</sup>Dedicated testing hardware used regularly during development.<br>
<sup>2</sup>get_terminal_info(): Startup *.MER file name is unavailable.<br>
<sup>3</sup>get_terminal_info(): Running *.MED file name is unavailable.<br>
<sup>4</sup>download() and reboot(): Reboot may be unavailable.<br>