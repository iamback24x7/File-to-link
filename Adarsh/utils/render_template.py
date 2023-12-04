from Adarsh.vars import Var
from Adarsh.bot import StreamBot
from Adarsh.utils.human_readable import humanbytes
from Adarsh.utils.file_properties import get_file_ids
from Adarsh.server.exceptions import InvalidHash
import urllib.parse
import aiofiles
import logging
import aiohttp


async def render_page(id, secure_hash):
    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(id))
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f'link hash: {secure_hash} - {file_data.unique_id[:6]}')
        logging.debug(f"Invalid hash for message with - ID {id}")
        raise InvalidHash
    src = urllib.parse.urljoin(Var.URL, f'{secure_hash}{str(id)}')
    
    if str(file_data.mime_type.split('/')[0].strip()) == 'video':
        async with aiofiles.open('Adarsh/template/req.html') as r:
            heading = 'Watch {}'.format(file_data.file_name)
            tag = file_data.mime_type.split('/')[0].strip()
            html = (await r.read()).replace('tag', tag) % (heading, file_data.file_name, src)
    elif str(file_data.mime_type.split('/')[0].strip()) == 'audio':
        async with aiofiles.open('Adarsh/template/req.html') as r:
            heading = 'Listen {}'.format(file_data.file_name)
            tag = file_data.mime_type.split('/')[0].strip()
            html = (await r.read()).replace('tag', tag) % (heading, file_data.file_name, src)
    else:
        async with aiofiles.open('Adarsh/template/dl.html') as r:
            async with aiohttp.ClientSession() as s:
                async with s.get(src) as u:
                    heading = 'Download {}'.format(file_data.file_name)
                    file_size = humanbytes(int(u.headers.get('Content-Length')))
                    html = (await r.read()) % (heading, file_data.file_name, src, file_size)
    current_url = f'{Var.URL}/{str(id)}/{file_data.file_name}?hash={secure_hash}'
    html_code = f'''

  <!-- Link to Plyr CSS -->
  <link rel="stylesheet" href="https://cdn.plyr.io/3.6.8/plyr.css">
  <style>
    body {
      font-family: 'Arial', sans-serif;
      background-color: #f3f3f3;
      margin: 0;
      padding: 0;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
    }

    .container {
      width: 95%; /* Increased width */
      max-width: 800px;
      margin: 0 auto;
    }

    .box-main {
      background-color: #ffffff;
      padding: 20px;
      border-radius: 15px;
      box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
    }

    video {
      width: 100%;
      border-radius: 10px;
    }

    .btn-primary {
      background-color: #007bff;
      color: #fff;
      transition: background-color 0.3s ease;
      border: none;
      border-radius: 10px;
      padding: 15px 20px;
      font-size: 18px;
      display: block;
      margin: 20px auto;
      text-align: center;
      text-decoration: none;
      cursor: pointer;
      width: 100%;
      box-sizing: border-box;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .btn-primary:hover {
      background-color: #0056b3;
    }

    button {
      padding: 15px;
      margin: 10px 0;
      border: none;
      border-radius: 10px;
      cursor: pointer;
      background-color: #28a745; /* Green color */
      color: #fff;
      transition: background-color 0.3s ease;
      width: 100%;
      box-sizing: border-box;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    button:hover {
      background-color: #218838; /* Darker green on hover */
    }

    footer {
 
      padding: 20px 0;
      border-radius: 15px;
      margin-top: 20px;
    }
  </style>


  <div class="container">
    <div class="box-main">
      <!-- Plyr Video Player -->
      <video id="player" class="playerbtns" controls="">
        <source src="{current_url}" type="video/mp4">
        <source src="{current_url}" type="video/ogg">
        Your browser does not support HTML5 video.
      </video>

      <div class="row">
        <div class="col-md-6">
          <p class="done"></p>
          <center><b>This link expires after 24 hours.</b></center>
          <p></p>
          <b>
            <a href="{current_url}" type="button" id="demo" class="btn btn-primary btn-block mb-4">
              Download Now
            </a>
          </b>
        </div>
      </div>

      <script>
        var url = "{current_url}";
        url = url.toLowerCase();
        if ((url.indexOf(".mp4") == -1) &&
            (url.indexOf(".avi") == -1) &&
            (url.indexOf(".mkv") == -1) &&
            (url.indexOf(".mov") == -1) &&
            (url.indexOf(".m3u8") == -1) &&
            (url.indexOf(".webm") == -1))
        {
            var btns = document.getElementsByClassName("playerbtns");
            for (x=0;x<btns.length;x++) {
                btns[x].style.display = "none";
            }
        }
      </script>

      <center>
        <button onclick="window.location.href='vlc://{current_url}'">👀 VLC Player</button>
        <button onclick="window.location.href='playit://playerv2/video?url={current_url}&amp;title=<TMPL_VAR file_name>'">👀 Playit app</button>
        <button onclick="window.location.href='intent:{current_url}#Intent;package=com.mxtech.videoplayer.ad;S.title=<TMPL_VAR file_name>;end'">👀 MX Player</button><br>
      </center>

      <br>

      <footer class="py-5 text-center wow animated zoomIn">
        <div class="container">
          <p class="mt-0 mb-0">
            <span id="credits"></span>
          </p>
        </div>
      </footer>
    </div>
  </div>

  <!-- Plyr JavaScript -->
  <script src="https://cdn.plyr.io/3.6.8/plyr.js"></script>
  <script>
    const player = new Plyr('#player');
  </script>




'''

    html += html_code    
    return html
