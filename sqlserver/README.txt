These folders contain add-ins for your SQL Server database to support 
additional Django features.

Regular Expression support:
* regex_clr contains a .NET (2.0) assembly that adds regex user functions
* regex_vbscript contains regex user functions implemented via VBScript

In order to enable regex support in trunk-django, you will need to manually
apply an appropriate patch (via TortoiseSVN or other tool) from the 
django-patches folder.
