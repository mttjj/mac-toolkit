on run argv
	set vPath to item 1 of argv
	set theFolder to POSIX file vPath as string
	
	tell application "Contacts"
		
		launch
		
		repeat with cardPerson in people
			
			set nameOfvCard to name of cardPerson & ".vcf"
			set theFile to ((POSIX file (vPath & "/" & nameOfvCard)) as string)
			
			set outFile to (open for access file theFile with write permission)
			
			write (vcard of cardPerson as text) to outFile starting at eof as Çclass utf8È
			
			close access outFile
			
		end repeat
		
		quit
		
	end tell
	
end run