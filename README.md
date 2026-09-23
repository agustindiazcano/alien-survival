# Alien Survival

Alien Survival es un prototipo experimental de juego web desarrollado utilizando **Babylon.js** (WebGL). 

## Descripción

El juego es un **survival de acción por oleadas (wave-based survival)** en el que el jugador debe sobrevivir a ataques constantes de enemigos alienígenas. A medida que se progresa, las oleadas se vuelven más difíciles, requiriendo reflejos rápidos y una buena gestión de los recursos.

### Mecánicas Principales

*   **Oleadas de Supervivencia:** Sobrevive a múltiples oleadas de enemigos. La dificultad (salud y daño de los enemigos, frecuencia de aparición) aumenta en cada oleada.
*   **Sistema de Progresión (RPG Lite):** Los enemigos derrotados sueltan oro y orbes de experiencia (XP). Al subir de nivel, la salud del jugador se restaura.
*   **Tienda y Mejoras:** Entre oleadas o durante el juego, el jugador puede acceder a una tienda para gastar el oro recolectado en:
    *   Mejorar el daño y la cadencia de fuego del rifle básico.
    *   Comprar botiquines de salud y armadura.
    *   Adquirir nuevas armas (Lanzallamas, Plasma, Láser).
    *   Comprar y mejorar **drones aliados** que pueden curar al jugador o atacar con misiles a los enemigos cercanos.
*   **Armamento Variado:** Diferentes armas con mecánicas de disparo y daño únicas (desde ráfagas rápidas hasta daño en área o rayos láser continuos).
*   **Soporte Multiplataforma:** Controles adaptados para jugar tanto en **Escritorio (Desktop)** con teclado y ratón, como en **Dispositivos Móviles (Mobile)**.

## Tecnologías Utilizadas

*   HTML5 / CSS3 / JavaScript
*   [Babylon.js](https://www.babylonjs.com/) para el renderizado 3D y las físicas.
*   Babylon GUI para la interfaz de usuario (HUD, barras de vida, radar, tienda).
