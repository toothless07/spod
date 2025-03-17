<h1>SPOD: Spotify cover-art display</h1>
Displaying cover art of current playing song on spotify on an e-paper display.
Leverage the spotify to leverage the information about current playing song and convert it into a beautiful art and display it on an e-paper display

<h2>Hardware Used:</h2>
<ul>
<li>Raspberry Pi zero 2 W</li>
<li>Waveshare 7 colour e-ink display (ACeP 7 colour) (800*480 Pixels) (https://hubtronics.in/7.3inch-e-paper-hat-f)</li>
<li>e-Paper Raw Panel Driver HAT for ACeP 7-Color E-Paper Display (https://hubtronics.in/e-paper-raw-panel-driver-hat)</li>
</ul>

<h2>Note:</h2>
<ul>
<li>Starter code for any board and display can be found under examples of github repo (https://github.com/waveshareteam/e-Paper)</li>
<li>use Raspberry Pi since the hat is easily available</li>
<li>well supported libraries</li>
</ul>

<h2>Important Links:</h2>
<ul>
<li>Setting up wifi connections:</li>
  <ul>
    <li>https://www.thedigitalpictureframe.com/how-to-add-a-second-wifi-network-to-your-raspberry-pi/</li>
  </ul>
    
    ```bash
    cd /etc/NetworkManager/system-connections/
    ls
    each one is a wifi connection data
    ```
</ul>
<h2>GITHUB Repos refrerences:</h2>
<ul>
<li>https://github.com/matthewbadeau/7-Color-E-paper-Image-converter (for converting the image in 7 color image)</li>
<li>https://github.com/waveshareteam/e-Paper (displaying image on the waveshare display)</li>
</ul>
