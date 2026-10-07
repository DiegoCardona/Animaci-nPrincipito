# El Principito: página uno

Animación narrativa en 2D, estilo *low poly* con bordes de tinta marcados y colores vivos, de la primera página de *El Principito* (capítulo I). El texto aparece palabra por palabra dentro de la escena, en paneles de papel y bocadillos.

## Cómo verla

Abre `index.html` en cualquier navegador moderno. No necesita compilación ni dependencias; solo carga las fuentes Grandstander y Nunito desde Google Fonts (si no hay conexión, usa fuentes del sistema).

Controles:

- Clic en la escena o barra espaciadora: pausar o reanudar
- ← / →: retroceder o avanzar 5 segundos
- R: volver a empezar
- M o botón del altavoz: activar o silenciar la música
- Barra inferior: saltar a cualquier momento

## Escenas (≈1 min 44 s)

1. Portada: el principito sobre su asteroide.
2. El libro *«Historias vividas»* se abre.
3. En la selva, una boa se traga a una fiera.
4. Seis meses de digestión, con ciclos de día y noche.
5. El niño traza su dibujo número 1 con un lápiz de color.
6. Las personas mayores: «¿Por qué habría de dar miedo un sombrero?».
7. El «sombrero» se revela como una boa.
8. Dibujo número 2: el elefante dentro de la boa. «Siempre necesitan explicaciones».
9. Cierre.

## Música

La música ambiente se genera en el navegador con Web Audio, sin archivos de audio: pads suaves, notas de caja de música, bajo y reverberación. Cada escena tiene su ánimo: soñador en la portada y el cierre, marimba y maracas en la selva, una nana lenta durante la digestión, un arpegio juguetón con los dibujos y las personas mayores, y acordes misteriosos al revelar la boa.

Los navegadores no permiten sonido sin un gesto del usuario, así que la música empieza con el primer toque, clic o tecla (o con el botón «Activar música»). Se detiene al pausar.

## Sobre el texto

El texto es una traducción libre al español hecha a partir del original francés *Le Petit Prince* (Antoine de Saint-Exupéry, 1943), para no reproducir una traducción editorial con derechos vigentes.

## Técnica

Todo se dibuja en un único `<canvas>` a 1920×1080 que se escala al tamaño de la ventana. Cada forma se divide en triángulos con sombreado según una luz fija y se contornea con tinta. Las escenas son funciones del tiempo, lo que permite saltar a cualquier punto.
