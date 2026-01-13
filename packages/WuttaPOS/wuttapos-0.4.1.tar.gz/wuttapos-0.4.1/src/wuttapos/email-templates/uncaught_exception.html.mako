## -*- coding: utf-8; -*-
<html>
  <body>
    <h2>Uncaught Exception</h2>

    <p>
      The following error was not handled properly.&nbsp; Please investigate and fix ASAP.
    </p>

    <h3>Context</h3>

    % if extra_context is not Undefined and extra_context:
        <ul>
          % for key, value in extra_context.items():
              <li>
                <span style="font-weight: bold;">${key}:</span>
                ${value}
              </li>
          % endfor
        </ul>
    % else:
        <p>N/A</p>
    % endif

    <h3>Error</h3>

    <p style="font-weight: bold; padding-left: 2rem;">
      ${error}
    </p>

    <h3>Traceback</h3>

    <pre class="indent">${traceback}</pre>

  </body>
</html>
