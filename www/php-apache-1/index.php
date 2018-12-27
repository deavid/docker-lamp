<html>
 <head>
  <title>Prueba de PHP</title>
 </head>
 <body>
 <?php
$filename = './uploads/test.txt';
echo '<p>Hola Mundo</p>';
file_put_contents($filename, 'Time: ' . time() . "\n", FILE_APPEND);
echo '<pre>';
echo file_get_contents($filename);
echo '</pre>';

 ?>
 </body>
</html>
