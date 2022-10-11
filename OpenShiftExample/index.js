const figlet = require('figlet');
const express = require('express');

const app = express();
app.enable('trust proxy');

const title = figlet.textSync('OpenShift demo: Figlet app on MOC', { font: 'Doom' });

const info = `${title}\n`
  + '              Bringing ChRIS (Storage and Compute) Fully to OpenShift and Kubernetes\n'
  + "                            Boston University EC 528 project\n"
  + "                              and the Mass Open Cloud\n"

app.get('/', (req, res) => {
  res.type('text/plain');
  if (!req.query.message) {
    res.status(400).send(
      info + '\n\n' +
      `usage: curl '${req.protocol}://${req.hostname}${req.path}?message=YOUR+TEXT'`
    );
    return;
  }
  figlet.text(req.query.message, {
    font: 'Doom',
  }, function(err, data) {
    if (err) {
        console.dir(err);
        return;
    }
    res.status(200).send(data);
  });
});

app.listen(process.env.PORT || 8080);
