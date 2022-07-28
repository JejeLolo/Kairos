param (
    [string]$taskname = ""   
 )

 'UnlockScheduledTask.ps1  Version 1.0'
 if ($taskname -eq '') {
    ''
    'No task name specified.'
    'SDDL for all tasks will be displayed.'
    ''
 } else {
    $batFile = "$env:TEMP\Set-A-Task-Free.bat"           # if you don't like my names, you can change them here. 
    $updateTaskName = 'Set-A-Task-Free'
    ''
    "SDDL for $taskname will be updated via $batfile"
    ''
 }
 $wmisdh = new-object system.management.ManagementClass Win32_SecurityDescriptorHelper 
 $subkeys = Get-childitem "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree"
 foreach ($key in $subkeys) {
    if ($taskname -eq '') {              # if blank, show SDDL for all tasks 
        ''
        $key.PSChildName
        $task = Get-ItemProperty $($key.name).replace("HKEY_LOCAL_MACHINE","HKLM:")
        $sddl = $wmisdh.BinarySDToSDDL( $task.SD ) 
        $sddl['SDDL']        
    
    } else {
        if ($key.PSChildName -eq $taskname) {
            ""
            $key.PSChildName
            $task = Get-ItemProperty $($key.name).replace("HKEY_LOCAL_MACHINE","HKLM:")
            $sddl = $wmisdh.BinarySDToSDDL( $task.SD ) 
            $sddl['SDDL']
            ''
            'New SDDL'
            $newSD = $sddl['SDDL'] +  '(A;ID;0x1301bf;;;AU)'          # add authenticated users read and execute
            $newSD                                                    # Note: cacls /s will display the SDDL for a file. 
            $newBin = $wmisdh.SDDLToBinarySD( $newsd )
            [string]$newBinStr =  $([System.BitConverter]::ToString($newBin['BinarySD'])).replace('-','') 
            
            # Administrators only have read permissions to the registry vlaue that needs to be updated.
            # We will create a bat file with a reg.exe command to set the new SD.
            # The bat file will be invoked by a scheduled task that runs as the system account.
            # The bat file can also be reused if the task is deployed to other machines. 
            ''
            "reg add ""HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree\{0}"" /f /v SD /t REG_BINARY /d {1}" -f $key.PSChildName, $newBinStr
            "reg add ""HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree\{0}"" /f /v SD /t REG_BINARY /d {1}" -f $key.PSChildName, $newBinStr  | out-file -Encoding ascii $batfile  
            ''

            SCHTASKS /Create /f /tn "$updateTaskName" /sc onstart  /tr "cmd.exe /c $batfile" /ru system 
            SCHTASKS /run /tn "$updateTaskName"
            $count = 0
            while ($count -lt 5) {
                start-sleep 5
                $count++
                $(Get-ScheduledTask -TaskName $updateTaskName).State
                if ($(Get-ScheduledTask -TaskName $updateTaskName).State -eq 'Ready') {
                    $count = 99            # it's ok to procees
                }
            }
            if ($count -ne 99) {
                "Error! The $updateTaskName task is still running. "
                'It should have ended by now.'
                'Please investigate.'
                return
            }
            SCHTASKS /delete /f /tn "$updateTaskName"
            ''
            'Security has been updated. Test it.'
        }
    }      
 }