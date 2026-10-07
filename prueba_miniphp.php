<?php
function presentar($persona) {
    echo "Bienvenido, " . $persona;
}

$anios = 21;
if ($anios >= 18) {
    presentar("Carlos");
} else {
    echo 'Aún no es mayor';
}
?>
