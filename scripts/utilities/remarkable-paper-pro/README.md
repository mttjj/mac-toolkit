# Remarkable Paper Pro

## Dev Mode
1. Settings > General > Software > Developer Mode
2. Follow instructions for resetting the device to put it into Dev Mode

## SSH Setup
1. Connect to computer with USB
2. Settings > Help > Copyrights and Licenses
3. Find local IP address (probably `10.11.99.1`)
4. Open terminal: `ssh root@10.11.99.1`
5. Log in using password found on Copyrights and Licenses page
6. Can enable `rm-ssh-over-wlan on` if desired but over USB is sooooo much faster

## Conveniences
### SSH Keys
Configure SSH keys to connect without having to enter password every time.
1. On Mac
   1. `ssh-keygen -t ed25519 -C "remarkable@matthewjj.com"`
   2. Hit Enter a few times until it’s saved
   3. `cat ~/.ssh/id_ed25519.pub`
   4. Copy the entire line to clipboard
2. Connect to reMarkable via SSH
   1. `ssh root@10.11.99.1`
   2. `cd ~/.ssh/`
   3. `nano authorized_keys`
   4. Paste the copied line into the file. Ctrl+x > Y > enter to save
3. On Mac
   1. `nano ~/.ssh/config`
   2. ```
      Host rmpp
      	Hostname 10.11.99.1
      	User root
      	ForwardX11 no
      	ForwardAgent no
      ```
   3. Ctrl+x > Y > enter to save

Now, can connect to rMPP with `ssh rmpp`

## Backup
`backup_rmpp.py` (in backup directory) can be run to back up all remarkable documents in the Personal and Work folders.

## Scripts
- `rmpp_upload_file.sh` - can be used to upload large files to the rmpp directly without using the cloud
- `rmpp_replace_suspended_image.sh` - can be used to replace the custom suspended.png file that gets overwritten when the RMPP software is updated

## Sources
rm-upload script: https://github.com/adaerr/reMarkableScripts/blob/master/pdf2remarkable.sh

https://www.informaticar.net/how-to-connect-to-remarkable-paper-pro-via-ssh/

https://www.informaticar.net/how-to-change-sleep-screen-is-sleeping-on-remarkable-paper-pro/

https://www.informaticar.net/how-to-backup-files-on-remarkable-paper-pro-without-cloud/

https://www.informaticar.net/how-to-transfer-files-to-remarkable-paper-pro-without-cloud/