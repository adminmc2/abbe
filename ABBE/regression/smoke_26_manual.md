# Smoke Manual — Bloque 2.6

## Objetivo
Validar en navegador real que el aislamiento de historial por usuario funciona correctamente en dispositivo compartido.

## Precondiciones
- Servidor ABBE corriendo en `http://localhost:7862` (v4.11.0+)
- Chrome/Safari con DevTools disponible
- Hard refresh (Cmd+Shift+R) para cargar JS actualizado
- Local Storage limpio para `localhost:7862`

## Flujo de prueba

### Ronda 1 — Usuario A
1. Login: `qa_smoke_a` / `Prisma`
2. Hacer 2 consultas (ej: "¿Qué es el CTM Renal?", "indicaciones Metabólica")
3. F5 (recargar)
4. **Verificar:** las 2 búsquedas reaparecen en welcome screen

### Ronda 2 — Usuario B
5. Logout (botón salir)
6. Login: `qa_smoke_b` / `Prisma`
7. Hacer 2 consultas **diferentes** (ej: "objeción de precio", "mecanismo de acción")
8. F5 (recargar)
9. **Verificar:** solo ve sus 2 búsquedas, **nada de qa_smoke_a**

### Ronda 3 — Vuelta a A
10. Logout
11. Login: `qa_smoke_a` / `Prisma`
12. **Verificar:** recupera **solo sus 2 búsquedas originales**

## Puntos de verificación en DevTools

### Local Storage (Application tab)
- `abbe_user` → nombre del usuario activo
- `abbe_logged_in` → `true`
- `abbe_recent_searches:abbe_above_pharma:qa_smoke_a` → items de A
- `abbe_recent_searches:abbe_above_pharma:qa_smoke_b` → items de B
- Keys **separadas**, sin contaminación cruzada

### Network (Fetch/XHR)
- `POST /api/history/load` → payload con `username` y `app_id: "abbe_above_pharma"`
- `POST /api/history/save` → payload con `username`, `searches[]`, `app_id`
- Respuestas separadas por usuario

### Console
- Sin errores JS
- Logs `[Sync]` muestran operaciones correctas

## Criterios de aceptación
| Criterio | Esperado |
|----------|----------|
| Sesión persiste tras F5 | Login no se pierde |
| Búsquedas se acumulan | Todas las queries guardadas |
| Keys separadas en localStorage | Una key por usuario |
| Sin contaminación A↔B | Cada usuario solo ve lo suyo |
| Logout limpia chat y contexto | Sin flash visual del anterior |
| Network muestra username+app_id | Requests correctos |

## Resultado
- [ ] PASS — todos los criterios verificados
- [ ] FAIL — indicar qué criterio falló

## Fecha de última ejecución
2026-04-23 — v4.9.3 — PASS (qa_26_a / qa_26_b, Chrome localhost)
