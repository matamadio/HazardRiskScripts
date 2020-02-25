Sub Append_CSV_File()
    
    Dim csvFileName As Variant
    Dim destCell As Range
    
    Set destCell = Worksheets("Sheet1").Cells(Rows.Count, "A").End(xlUp).Offset(1)      'CHANGE SHEET NAME
    
    csvFileName = Application.GetOpenFilename(FileFilter:="CSV Files (*.csv),*.csv", Title:="Select a CSV File", MultiSelect:=False)
    If csvFileName = False Then Exit Sub
    
    With destCell.Parent.QueryTables.Add(Connection:="TEXT;" & csvFileName, Destination:=destCell)
        .TextFileStartRow = 2
        .TextFileParseType = xlDelimited
        .TextFileCommaDelimiter = True
        .Refresh BackgroundQuery:=False
    End With
    
    destCell.Parent.QueryTables(1).Delete

End Sub