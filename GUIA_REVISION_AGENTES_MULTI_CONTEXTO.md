# GUÍA DE REVISIÓN DE SISTEMAS DE AGENTES IA MULTI-CONTEXTO

> Marco reusable para analizar desarrollos con agentes IA aplicados a cualquier dominio.  
> Sirve para proyectos con uno o varios agentes, con o sin RAG, con frontend, API o canales conversacionales.

---

## 1. Objetivo

Esta guía define **cómo revisar**, **qué pedir**, **qué considerar bloqueante** y **cómo cerrar** una revisión de un sistema de agentes IA.

Su propósito es evitar:

- decisiones ambiguas
- cierres sin evidencia
- mezclar problemas de arquitectura con problemas de contenido o UX
- arrastrar residuos de un contexto anterior a uno nuevo
- validar respuestas “aparentemente buenas” sin trazabilidad real

---

## 2. Cuándo aplicar esta guía

Aplicar esta guía cuando exista al menos uno de estos casos:

- un asistente conversacional con LLM
- un sistema multi-agente con router u orquestador
- un agente con RAG, tools o acceso a fuentes externas
- una migración de dominio, marca o catálogo
- una adaptación de un agente previo a otro cliente, vertical o contexto
- una revisión de calidad previa a release

---

## 3. Principios de revisión

1. **No pasar al siguiente bloque hasta cerrar el actual.**
2. Todo cierre requiere 4 evidencias:
   - qué cambió
   - dónde cambió
   - cómo se validó
   - evidencia concreta
3. Diferenciar siempre entre:
   - problema **activo**
   - problema **visible**
   - problema **inerte**
   - problema **fuera de alcance**
4. No aceptar “parece funcionar” como criterio de cierre.
5. No mezclar:
   - arquitectura
   - routing
   - grounding/RAG
   - UX/frontend
   - documentación/versionado
6. Toda revisión debe dejar trazabilidad de:
   - hallazgo
   - impacto
   - decisión
   - estado

---

## 4. Tipos de hallazgo

| Tipo | Definición | Bloquea |
|---|---|---|
| Crítico | Rompe seguridad, veracidad, control de dominio o superficies públicas activas | Sí |
| Mayor | Afecta precisión, routing, grounding, UX clave o documentación operativa | Sí |
| Menor | Problema real pero acotado, sin romper el flujo principal | Depende |
| Inerte | Comentario, residuo o inconsistencia sin impacto runtime ni exposición real | No |
| Fuera de alcance | Punto válido pero no perteneciente al bloque activo | No en ese bloque |

---

## 5. Evidencia mínima que debe pedirse

Antes de cerrar cualquier punto, pedir al menos uno de estos conjuntos:

### Opción A — evidencia técnica directa
- `git diff`
- archivos completos
- fragmentos exactos de código
- salida de grep o búsqueda global
- logs o respuestas de endpoints

### Opción B — evidencia funcional
- capturas
- salida de UI
- requests/responses
- trazas
- reproducibilidad paso a paso

### Regla
Si el problema está en **runtime**, la evidencia debe venir de:
- código ejecutado
- salida real
- trazas
- UI real

No basta con resúmenes manuales si el archivo o diff puede revisarse directamente.

---

## 6. Artefactos mínimos a solicitar

Según el tipo de proyecto, pedir como mínimo:

### Base técnica
- entry point backend
- router/orquestador
- agentes implicados
- motor RAG o capa de grounding
- catálogo/configs/fuentes
- frontend principal si existe
- documentación operativa
- changelog o historial de versiones

### Validación
- endpoint de health/status
- prueba mínima reproducible
- grep de términos sensibles
- reporte de regresión si existe

### En migraciones de contexto
- inventario de residuos del dominio anterior
- lista de superficies públicas
- lista de textos visibles
- vocabulario operativo activo
- branding, assets y artefactos expuestos

---

## 7. Bloques estándar de revisión

## 7.1 Contexto, alcance y criterio de éxito
Validar:

- cuál es el problema de negocio
- quién es el usuario real
- qué decisiones toma el sistema
- qué no debe hacer
- cuál es el dominio vigente
- qué parte viene heredada de otro contexto

Preguntas clave:

- ¿Qué flujo real debe resolverse?
- ¿Qué dominio es el vigente?
- ¿Qué parte es nueva y qué parte es heredada?
- ¿Qué significa “cerrado” para este proyecto?

Bloquea si:

- el objetivo no está definido
- el dominio vigente no está fijado
- no existe criterio de aceptación

---

## 7.2 Datos, catálogo y fuentes de verdad
Validar:

- contratos de datos
- campos obligatorios
- fuentes válidas
- consistencia entre catálogo, KB y runtime
- reglas de actualización

Preguntas clave:

- ¿De dónde sale la verdad del sistema?
- ¿Existe catálogo explícito?
- ¿La KB tiene contrato estable?
- ¿Hay referencias cruzadas válidas?

Bloquea si:

- el sistema responde con datos no trazables
- catálogo y KB se contradicen
- no hay validación de integridad

---

## 7.3 Arquitectura y límites entre agentes
Validar:

- número de agentes y responsabilidad real
- separación de roles
- contratos entre componentes
- si el diseño aprobado se está respetando

Preguntas clave:

- ¿Cada agente tiene una responsabilidad clara?
- ¿Hay solapamiento de roles?
- ¿Hay lógica duplicada entre agentes?
- ¿Se está intentando resolver con prompts lo que debería resolverse con arquitectura?

Bloquea si:

- no hay límites claros entre agentes
- la arquitectura aprobada fue alterada sin decisión explícita
- un agente asume responsabilidades de otro sin control

---

## 7.4 Routing, orquestación y selección de agente
Validar:

- reglas de clasificación
- prioridad entre intención, frame, keywords y contexto
- fallback
- thresholds
- casos ambiguos

Preguntas clave:

- ¿El routing depende de intención real o de palabras sueltas?
- ¿Existe fallback coherente?
- ¿Los casos ambiguos están cubiertos?
- ¿La lógica está en reglas, modelo o mezcla incontrolada?

Bloquea si:

- el usuario cae en el agente incorrecto de forma sistemática
- el fallback no funciona
- el routing depende de heurísticas frágiles no justificadas

---

## 7.5 Grounding, RAG y uso de fuentes
Validar:

- estrategia de búsqueda
- ranking
- thresholds
- metadata boost
- trazabilidad de fragmentos usados
- política de no respuesta si no hay soporte

Preguntas clave:

- ¿La respuesta está grounded?
- ¿Se sabe por qué se eligió ese contexto?
- ¿Existe soporte documental suficiente?
- ¿El sistema inventa cuando no encuentra evidencia?

Bloquea si:

- no hay trazabilidad
- el sistema responde sin soporte suficiente
- el retrieval no discrimina bien por producto, tema o entidad

---

## 7.6 Políticas de respuesta y control de claims
Validar:

- claims permitidos
- comparativas
- restricciones regulatorias
- tono
- manejo de incertidumbre
- separación entre hecho, interpretación y sugerencia

Preguntas clave:

- ¿Qué puede afirmar el sistema?
- ¿Cuándo debe abstenerse?
- ¿Cómo maneja comparativas y competidores?
- ¿Qué claims requieren soporte explícito?

Bloquea si:

- el sistema hace claims no soportados
- compara sin política
- no distingue soporte documental de generación libre

---

## 7.7 Frontend, UX y desacople de contexto
Validar:

- textos visibles
- placeholders
- nombres hardcoded
- demos mostradas como datos reales
- branding heredado
- assets públicos
- superficies auxiliares accesibles por URL

Preguntas clave:

- ¿La UI representa estado real o demo?
- ¿Quedan nombres, avatares o usuarios fijos?
- ¿Hay residuos del contexto anterior visibles o activos?
- ¿Existen páginas auxiliares públicas no productivas?

Bloquea si:

- hay hardcodes visibles engañosos
- quedan superficies públicas con branding o copy anterior
- el frontend presenta datos demo como verdad del usuario

---

## 7.8 Seguridad, secretos y acceso
Validar:

- credenciales
- secretos en cliente
- permisos
- endpoints públicos
- variables de entorno
- tratamiento de datos sensibles

Preguntas clave:

- ¿Hay secretos hardcoded?
- ¿Qué puede verse desde cliente?
- ¿Qué endpoints están expuestos?
- ¿Hay riesgo aceptado o riesgo no documentado?

Bloquea si:

- hay secretos sensibles en cliente sin decisión explícita
- existen endpoints expuestos sin control
- hay acceso indebido a datos o acciones

---

## 7.9 Observabilidad, trazas y depuración
Validar:

- logs útiles
- trazas por request
- audit trail
- identificación de fuente
- motivo de selección de agente o contexto

Preguntas clave:

- ¿Se puede explicar qué pasó?
- ¿Se puede reproducir un fallo?
- ¿Se puede distinguir error de datos, routing o LLM?

Bloquea si:

- no existe forma de auditar decisiones clave
- no hay trazabilidad para investigar errores

---

## 7.10 Documentación, versionado y operabilidad
Validar:

- versión visible
- versión backend
- changelog
- README
- artefactos de regresión
- nombres de archivos vigentes
- consistencia entre documentación y runtime

Preguntas clave:

- ¿La versión visible coincide con la operativa?
- ¿La documentación describe el sistema real?
- ¿Quedan referencias a artefactos obsoletos?
- ¿La guía de operación sigue vigente?

Bloquea si:

- documentación y runtime están desalineados
- el versionado visible es incorrecto
- se usan referencias antiguas como si siguieran vigentes

---

## 8. Riesgos típicos en migraciones entre contextos

Vigilar especialmente:

- branding anterior en frontend o runtime
- vocabulario legado aún activo en reglas o prompts
- assets o páginas viejas accesibles por URL
- demos heredadas mostradas como producción
- comparativas o claims del contexto anterior
- configuraciones de producto recicladas sin limpieza
- rutas, nombres de artefactos o cache-busters desalineados
- lógica de negocio heredada que ya no corresponde al nuevo dominio

---

## 9. Qué se considera “cerrado”

Un punto solo se considera cerrado si:

1. el problema fue entendido y delimitado
2. existe evidencia técnica o funcional suficiente
3. el cambio real ya está implementado
4. no queda contradicción entre resumen y archivos
5. el impacto cruzado fue revisado
6. el criterio de cierre está escrito de forma explícita

---

## 10. Qué no debe aceptarse como cierre

No aceptar como cierre:

- “ya debería estar”
- “en local se ve bien”
- “solo falta ajustar el review”
- “el resumen dice que está hecho”
- “lo revisamos luego”
- “no está enlazado, así que no importa”
- “el modelo lo resolverá”
- “es solo un comentario” cuando sigue en una superficie pública o runtime relevante

---

## 11. Plantilla breve para abrir una revisión

Usar esta estructura:

### Contexto operativo
- dominio vigente:
- usuario objetivo:
- problema que resuelve:
- arquitectura aprobada:
- restricciones:
- punto activo:

### Estado global
| Bloque | Estado | Nota |
|---|---|---|

### Punto activo
- objetivo real:
- alcance mínimo:
- evidencia mínima requerida:
- criterio de cierre:
- bloqueos conocidos:

---

## 12. Plantilla breve para documentar hallazgos

| # | Archivo / superficie | Hallazgo | Tipo | Impacto | Decisión | Estado |
|---|---|---|---|---|---|---|

Estados sugeridos:
- pendiente
- en curso
- validado
- no bloqueante
- fuera de alcance
- cerrado

---

## 13. Plantilla breve para cierre de un punto

### Cierre alcanzado
- qué cambió:
- dónde cambió:
- cómo se validó:
- evidencia concreta:

### Impacto cruzado
- reabre otro punto: sí / no
- afecta documentación: sí / no
- requiere versión nueva: sí / no

### Decisión actual
- estado:
- siguiente punto:
- bloqueo restante:

---

## 14. Matriz simple de decisión

| Situación | Decisión |
|---|---|
| Hallazgo activo en runtime o superficie pública | No cerrar |
| Resumen dice “hecho” pero el archivo no lo confirma | No cerrar |
| Código corregido pero documentación desalineada | Cierre parcial |
| Todo alineado y con evidencia suficiente | Cerrar |
| Hay residuos inertes sin impacto real ni exposición | Documentar y no bloquear |
| El punto pertenece a otro bloque | Diferir con referencia explícita |

---

## 15. Recomendación operativa

En revisiones largas, mantener siempre:

- **un solo punto activo**
- **un inventario trazable**
- **una definición de bloqueante**
- **un criterio de cierre escrito**
- **un historial corto de decisiones ya fijadas**

Eso evita repetir discusiones y permite reutilizar la revisión en otros dominios.

---

## 16. Resultado esperado de esta guía

Aplicada correctamente, esta guía permite evaluar si un sistema de agentes:

- responde sobre el dominio correcto
- selecciona bien el agente o flujo
- usa fuentes confiables
- evita claims no soportados
- no arrastra residuos de otro contexto
- expone una UI/documentación coherente
- puede considerarse listo para operación o release