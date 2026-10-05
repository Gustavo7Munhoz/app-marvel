$names = @('Iron Man', 'Captain America', 'Thor', 'Hulk', 'Black Widow', 'Hawkeye', 'Mister Fantastic', 'Invisible Woman', 'Human Torch', 'Thing', 'Star-Lord', 'Gamora', 'Drax the Destroyer', 'Rocket Raccoon', 'Groot', 'Wolverine', 'Cyclops', 'Storm', 'Jean Grey', 'Beast', 'Baron Zemo', 'Songbird', 'Moonstone', 'Ikaris', 'Sersi', 'Thena')
$apiKey = "bbf8ecf304d2b89198f1e3ca3cd6a0433b6c74a3"

foreach ($name in $names) {
    # Replace spaces with %20
    $query = $name -replace ' ', '%20'
    $uri = "https://comicvine.gamespot.com/api/search/?api_key=$apiKey&format=json&query=$query&resources=character&limit=1"
    
    try {
        $res = Invoke-RestMethod -Uri $uri -UserAgent 'MarvelShieldCommandCenter/1.0'
        if ($res.results.Count -gt 0) {
            Write-Output "$name : $($res.results[0].id)"
        } else {
            Write-Output "$name : NOT FOUND"
        }
    } catch {
        Write-Output "$name : ERROR"
    }
}
