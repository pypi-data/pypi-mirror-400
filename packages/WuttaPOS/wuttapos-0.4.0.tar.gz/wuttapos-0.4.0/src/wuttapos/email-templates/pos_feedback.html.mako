## -*- coding: utf-8; -*-
<html>
  <head>
    <style type="text/css">
      label {
          display: block;
          font-weight: bold;
          margin-top: 1em;
      }
      p {
          margin: 1em 0 1em 1.5em;
      }
      p.msg {
          white-space: pre-wrap;
      }
    </style>
  </head>
  <body>
    <h1>User feedback from POS</h1>

    <label>User Name</label>
    <p>${user_name}</p>

    <label>Referring View</label>
    <p>${referrer}</p>

    <label>Message</label>
    <p class="msg">${message}</p>

  </body>
</html>
