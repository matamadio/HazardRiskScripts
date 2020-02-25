Sub MergeSheets()
    
    Dim HasHeaderRow As String * 1, SameWorkbook As String * 1
    Dim OPSheet As String
    Dim ToDir As String, FileName As String
    
 '******** Change Parameters in this section ****************
    'Set the values for HasHeaderRow and ToDir
    HasHeaderRow = "Y"
    SameWorkbook = "Y"
    OPSheet = "Result"
    
    'Set the Save Directory and File Name if result is not wanted in the same workbook
    If SameWorkbook <> "Y" Then
        ToDir = "C:\Junk\"
        FileName = "Combined"
    End If
'***************************************************************
    
    Call Merge(HasHeaderRow = "Y", SameWorkbook = "Y", OPSheet, ToDir, FileName)

End Sub

Sub Merge(ByVal HasHeaderRow As Boolean, ByVal SameWorkbook As Boolean, ByVal OPSheet As String, _
            ByVal ToDir As String, ByVal FileName As String)
    
    Dim i As Long, StartIndex As Long
    Dim ToPath As String
    Dim TWk As Workbook, SWk As Workbook
    Dim Ws As Worksheet
    Dim Rng As Range, NewCell As Range
    Dim StartExists As Boolean, x As Boolean
    
    Application.DisplayAlerts = False
    Application.ScreenUpdating = False
    
    Set SWk = ActiveWorkbook
    
    'Check for the existence of directory if output is needed in a different directory
    If SameWorkbook = False Then
        If Right(ToDir, 1) <> "\" Then
            ToDir = ToDir & "\"
        End If
        On Error Resume Next
            If Dir(ToDir) = "" Then
                MsgBox ToDir & " does not exist"
                Exit Sub
            End If
        On Error GoTo 0
        
        'Set the file name which is FileName_Current Date_Current Time
        ToPath = ToDir & FileName & "_" & Format(Date, "mmddyy") & "_" & Format(Time, "hhmmss")
        
        'Create the workbook where data needs to be copied
        Set TWk = Workbooks.Add
        Else
        Set TWk = SWk
    End If
    
    'Create OPSheet.
    On Error Resume Next
        Set Ws = TWk.Worksheets(OPSheet)
        If Err.Number <> 0 Then
            TWk.Worksheets.Add(Before:=TWk.Worksheets(1)).Name = OPSheet
        End If
    On Error GoTo 0
    'If OPSheet is existing, just clear it
    TWk.Worksheets(OPSheet).Cells.Clear
    
    'Check for existence of Start Sheet - If Start Sheet is there
    'then combine from Start otherwise combine from 1st sheet itself
    On Error Resume Next
    With SWk
        Set Ws = .Worksheets("Start")
            If Err.Number = 0 Then
                StartExists = True
                StartIndex = .Worksheets("Start").Index + 1
                Else
                'If within the same workbook, then we need to increase the index by 1 as first sheet is Result sheet now
                If SameWorkbook = True Then
                    StartIndex = 2
                    Else
                    StartIndex = 1
                End If
            End If
        On Error GoTo 0
        
        'Set the starting cell in first sheet of Target Workbook
        Set NewCell = TWk.Worksheets(OPSheet).Range("A1")
        
        For i = StartIndex To .Worksheets.Count
            'If there is a sheet names Finish, then stop combining
            If .Worksheets(i).Name = "Finish" Then Exit For
                If .Worksheets(i).Name <> "Result" Then
                'Check if the sheet is blank or not - If blank, no need to process
                If WorksheetFunction.CountA(.Worksheets(i).Cells) - WorksheetFunction.CountA(.Worksheets(i).Rows(1)) <> 0 Then
                    'x is a parameter which is set after first processing. In first processing, Header Row is not important
                    'But starting second processing, Header Row is Important. If Header Row is Y, then we should not select
                    'first row. Hence, x is set to True in this case.
                    If x = False Then
                        Set Rng = .Worksheets(i).UsedRange
                        Else
                        Set Rng = .Worksheets(i).UsedRange.Offset(1, 0)
                        Set Rng = Rng.Resize(Rng.Rows.Count - 1)
                    End If
                    'Copy the Range to Target Workbook
                    Rng.Copy NewCell
                    'Set the new cell to Next row of Column A in Target Workbook
                    Set NewCell = TWk.Worksheets(OPSheet).Cells(TWk.Worksheets(OPSheet).UsedRange.Rows.Count + 1, "A")
                    'Set NewCell = TWk.Worksheets(OPSheet).Cells(Rng(Rng.Cells.Count).Row + 1, "A")
                    If HasHeaderRow = True Then
                        x = True
                    End If
                End If
            End If
        Next i
    End With
    
    If SameWorkbook = False Then
        TWk.SaveAs FileName:=ToPath, FileFormat:=51
    End If
    
    Application.DisplayAlerts = True
    Application.ScreenUpdating = True
    Application.CutCopyMode = False

End Sub