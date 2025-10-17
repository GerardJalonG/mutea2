# Mutea2 🎙️

Bot de Discord para trackear el tiempo que los usuarios pasan muteados y ensordecidos en canales de voz.

## 📋 Descripción

Mutea2 es un bot de Discord que automáticamente rastrea y registra el tiempo que los miembros del servidor pasan con el micrófono muteado o los auriculares ensordecidos en los canales de voz. Proporciona comandos para consultar estadísticas individuales y clasificaciones del servidor.

## ✨ Características

- **Tracking automático**: Registra automáticamente cuando los usuarios se mutean o ensordecen
- **Persistencia de datos**: Utiliza SQLite para guardar los datos entre reinicios
- **Sesiones activas**: Continúa el tracking incluso si el bot se reinicia
- **Estadísticas personalizadas**: Consulta tu tiempo total muteado y ensordecido
- **Rankings**: Ve quién está más tiempo muteado o ensordecido en el servidor
- **Comandos intuitivos**: Fácil de usar con comandos con prefijo `!`

## 🚀 Instalación

### Requisitos previos

- Python 3.8 o superior
- Una aplicación de Discord Bot con token (obtener en [Discord Developer Portal](https://discord.com/developers/applications))

### Pasos de instalación

1. **Clona el repositorio**
   ```bash
   git clone https://github.com/GerardJalonG/mutea2.git
   cd mutea2
   ```

2. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configura el token del bot**
   
   Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:
   ```env
   DISCORD_TOKEN=tu_token_aqui
   ```

4. **Ejecuta el bot**
   ```bash
   python bot.py
   ```

## 🎮 Comandos

### Comandos de usuario

- **`!tiempo [@usuario]`**
  - Muestra el tiempo total que un usuario ha estado muteado y ensordecido
  - Si no se especifica usuario, muestra tu propia estadística
  - Ejemplo: `!tiempo` o `!tiempo @JuanPerez`

- **`!topmute [límite]`**
  - Muestra el top de usuarios que más tiempo han estado muteados
  - Límite por defecto: 10 usuarios
  - Ejemplo: `!topmute` o `!topmute 20`

- **`!topdeaf [límite]`**
  - Muestra el top de usuarios que más tiempo han estado ensordecidos
  - Límite por defecto: 10 usuarios
  - Ejemplo: `!topdeaf` o `!topdeaf 20`

- **`!ping`**
  - Verifica que el bot está respondiendo
  - Responde con "🏓 Pong!"

- **`!ayudame`**
  - Muestra la lista de comandos disponibles

### Comandos de administrador

- **`!reset_totals`**
  - Resetea todas las estadísticas del servidor
  - **Requiere**: Permisos de administrador
  - **Advertencia**: Esta acción es irreversible

## 🔧 Configuración

### Intents necesarios

El bot requiere los siguientes intents de Discord:
- `guilds`: Para acceso a la información del servidor
- `members`: Para resolver nombres de usuarios
- `voice_states`: Para detectar cambios en estados de voz
- `message_content`: Para procesar comandos con texto

Estos intents deben estar habilitados en el [Discord Developer Portal](https://discord.com/developers/applications) en la sección "Bot" de tu aplicación.

### Base de datos

El bot crea automáticamente un archivo `voice_times.db` en SQLite que contiene:
- **Tabla `totals`**: Acumuladores de tiempo muteado y ensordecido por usuario y servidor
- **Tabla `active_sessions`**: Sesiones activas para persistencia entre reinicios

## 📊 Funcionamiento

El bot detecta:
- **Mute**: Tanto el mute del servidor como el self-mute del usuario
- **Deaf**: Tanto el ensordecido del servidor como el self-deaf del usuario

El tracking comienza automáticamente cuando un usuario:
- Se mutea o ensordece en un canal de voz
- El bot acumula el tiempo hasta que el usuario desmutea o desensordece

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:
1. Haz un fork del proyecto
2. Crea una rama para tu característica (`git checkout -b feature/nueva-caracteristica`)
3. Haz commit de tus cambios (`git commit -m 'Añadir nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 👤 Autor

**Gerard Jalon**
- GitHub: [@GerardJalonG](https://github.com/GerardJalonG)

## 🐛 Reportar problemas

Si encuentras algún bug o tienes alguna sugerencia, por favor abre un [issue](https://github.com/GerardJalonG/mutea2/issues) en GitHub.

---

¡Disfruta usando Mutea2! 🎉
