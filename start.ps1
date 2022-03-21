while($true){
python $PSScriptRoot\scraper.py
Start-Sleep -Seconds (60*60*2)
}