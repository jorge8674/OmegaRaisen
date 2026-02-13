# 🎯 MASTER PROMPT: SISTEMA DE AUTOMATIZACIÓN DE REDES SOCIALES ENTERPRISE
## Ultra-Advanced Agent Instructions | Instrucciones Ultra-Avanzadas para Agente

---

## 📋 CONTEXT | CONTEXTO

**Project Name** | **Nombre del Proyecto**: Social Media Automation Platform  
**Philosophy** | **Filosofía**: No velocity, only precision 🐢💎  
**Language** | **Idioma**: ES/EN (Bilingual at all times | Bilingüe todo el tiempo)  
**Architecture** | **Arquitectura**: Domain-Driven Design (DDD), Modular, Maintainable  
**Code Quality** | **Calidad de Código**: Enterprise-grade, Production-ready

---

## 🚨 CRITICAL ARCHITECTURE RULES (NON-NEGOTIABLE)
## 🚨 REGLAS CRÍTICAS DE ARQUITECTURA (NO NEGOCIABLES)

### ⚡ ABSOLUTE RULES | REGLAS ABSOLUTAS

```typescript
/**
 * These rules are MANDATORY and have ZERO exceptions
 * Estas reglas son OBLIGATORIAS y tienen CERO excepciones
 */

1. ✅ MAX 200 LINES PER FILE (NO EXCEPTIONS)
   ✅ MÁXIMO 200 LÍNEAS POR ARCHIVO (SIN EXCEPCIONES)
   - If approaching 200 lines → Split into modules
   - Si se acerca a 200 líneas → Dividir en módulos
   - Use barrel exports (index.ts) to organize
   - Usar barrel exports (index.ts) para organizar

2. ✅ SEPARATION OF CONCERNS (STRICT)
   ✅ SEPARACIÓN DE RESPONSABILIDADES (ESTRICTA)
   - 1 file = 1 responsibility = 1 purpose
   - 1 archivo = 1 responsabilidad = 1 propósito
   - No mixing concerns (logic + UI + data)
   - No mezclar responsabilidades (lógica + UI + datos)

3. ✅ DRY PRINCIPLE (ZERO DUPLICATION)
   ✅ PRINCIPIO DRY (CERO DUPLICACIÓN)
   - Never copy-paste code
   - Nunca copiar-pegar código
   - Extract shared logic to utilities
   - Extraer lógica compartida a utilidades
   - Create reusable abstractions
   - Crear abstracciones reutilizables

4. ✅ TYPE SAFETY (STRICT MODE)
   ✅ SEGURIDAD DE TIPOS (MODO ESTRICTO)
   - TypeScript strict: true
   - Zero 'any' types (FORBIDDEN)
   - Cero tipos 'any' (PROHIBIDO)
   - Zero 'as any' casts (FORBIDDEN)
   - Cero 'as any' casts (PROHIBIDO)
   - Zero 'unknown' without proper narrowing
   - Cero 'unknown' sin proper narrowing
   - Create specific types for everything
   - Crear tipos específicos para todo

5. ✅ IMMUTABLE STATE (FUNCTIONAL UPDATES)
   ✅ ESTADO INMUTABLE (ACTUALIZACIONES FUNCIONALES)
   - No direct mutations
   - No mutaciones directas
   - Use spread operators: {...obj, field: value}
   - Usar operadores spread: {...obj, field: value}
   - Use array methods: map, filter, reduce
   - Usar métodos de array: map, filter, reduce

6. ✅ PURE FUNCTIONS (SIDE EFFECTS ISOLATED)
   ✅ FUNCIONES PURAS (EFECTOS SECUNDARIOS AISLADOS)
   - Pure functions for business logic
   - Funciones puras para lógica de negocio
   - Side effects in separate layers
   - Efectos secundarios en capas separadas
   - Predictable, testable code
   - Código predecible y testeable

7. ✅ SINGLE RESPONSIBILITY PRINCIPLE
   ✅ PRINCIPIO DE RESPONSABILIDAD ÚNICA
   - Each component does ONE thing
   - Cada componente hace UNA cosa
   - Each function does ONE thing
   - Cada función hace UNA cosa
   - Easy to understand and maintain
   - Fácil de entender y mantener

8. ✅ DOMAIN-DRIVEN DESIGN (DDD)
   ✅ DISEÑO DIRIGIDO POR DOMINIO (DDD)
   - Bounded contexts clearly defined
   - Contextos limitados claramente definidos
   - Ubiquitous language in code
   - Lenguaje ubicuo en código
   - Aggregates, Entities, Value Objects
   - Agregados, Entidades, Objetos de Valor
   - Domain logic separate from infrastructure
   - Lógica de dominio separada de infraestructura
```

---

## 🏗️ PROJECT STRUCTURE | ESTRUCTURA DEL PROYECTO

```
social-media-automation-platform/
├── apps/                           # Applications | Aplicaciones
│   ├── web/                       # Web Dashboard | Dashboard Web
│   │   ├── src/
│   │   │   ├── app/              # Next.js App Router
│   │   │   ├── components/       # React Components (max 200 lines each)
│   │   │   ├── hooks/            # Custom React Hooks
│   │   │   └── lib/              # Client utilities
│   │   └── package.json
│   ├── api/                       # Backend API | API Backend
│   │   ├── src/
│   │   │   ├── application/      # Use Cases | Casos de Uso
│   │   │   ├── domain/           # Domain Logic | Lógica de Dominio
│   │   │   ├── infrastructure/   # External Services | Servicios Externos
│   │   │   └── presentation/     # Controllers | Controladores
│   │   └── package.json
│   └── worker/                    # Background Jobs | Trabajos en segundo plano
│       ├── src/
│       │   ├── jobs/             # Job Definitions | Definiciones de Jobs
│       │   ├── schedulers/       # Cron Jobs | Trabajos Cron
│       │   └── processors/       # Job Processors | Procesadores
│       └── package.json
├── packages/                      # Shared Libraries | Librerías Compartidas
│   ├── core/                     # Core Business Logic | Lógica Core
│   │   ├── src/
│   │   │   ├── content/          # Content Generation | Generación de Contenido
│   │   │   ├── scheduling/       # Post Scheduling | Programación
│   │   │   ├── engagement/       # User Engagement | Engagement
│   │   │   └── analytics/        # Analytics Logic | Lógica de Analytics
│   │   └── package.json
│   ├── ai/                       # AI/ML Logic | Lógica AI/ML
│   │   ├── src/
│   │   │   ├── text-generation/  # Text AI | IA de Texto
│   │   │   ├── image-generation/ # Image AI | IA de Imagen
│   │   │   ├── video-generation/ # Video AI | IA de Video
│   │   │   └── response-ai/      # Smart Responses | Respuestas Inteligentes
│   │   └── package.json
│   ├── social-apis/              # Social Media APIs | APIs de Redes Sociales
│   │   ├── src/
│   │   │   ├── instagram/        # Instagram API Client
│   │   │   ├── facebook/         # Facebook API Client
│   │   │   ├── tiktok/           # TikTok API Client
│   │   │   ├── twitter/          # Twitter API Client
│   │   │   └── common/           # Shared API Logic | Lógica Compartida
│   │   └── package.json
│   ├── database/                 # Database Layer | Capa de Base de Datos
│   │   ├── src/
│   │   │   ├── repositories/     # Data Repositories | Repositorios
│   │   │   ├── models/           # Database Models | Modelos
│   │   │   └── migrations/       # DB Migrations | Migraciones
│   │   └── package.json
│   ├── ui/                       # Shared UI Components | Componentes UI Compartidos
│   │   ├── src/
│   │   │   ├── components/       # Reusable Components
│   │   │   ├── primitives/       # Base UI Elements
│   │   │   └── hooks/            # Shared Hooks
│   │   └── package.json
│   └── types/                    # Shared TypeScript Types | Tipos TS Compartidos
│       ├── src/
│       │   ├── entities/         # Domain Entities | Entidades de Dominio
│       │   ├── dtos/             # Data Transfer Objects | DTOs
│       │   └── enums/            # Enumerations | Enumeraciones
│       └── package.json
├── tools/                        # Development Tools | Herramientas de Desarrollo
│   ├── generators/               # Code Generators | Generadores de Código
│   └── scripts/                  # Utility Scripts | Scripts de Utilidad
├── .github/                      # GitHub Actions CI/CD
├── docker/                       # Docker Configuration | Configuración Docker
├── docs/                         # Documentation | Documentación
├── turbo.json                    # Turborepo Config
├── package.json                  # Root Package
└── tsconfig.base.json           # Base TypeScript Config
```

---

## 🎯 SYSTEM REQUIREMENTS | REQUISITOS DEL SISTEMA

### Core Features | Características Core

#### 1. 🎥 VIDEO GENERATION | GENERACIÓN DE VIDEO
```typescript
/**
 * Video generation from 15 to 120 seconds
 * Generación de video de 15 a 120 segundos
 */
interface VideoGenerationService {
  // Generate video with AI
  // Generar video con IA
  generateVideo(params: VideoGenerationParams): Promise<VideoResult>;
  
  // Supported durations: 15s, 30s, 60s, 90s, 120s
  // Duraciones soportadas: 15s, 30s, 60s, 90s, 120s
  validateDuration(seconds: number): boolean;
  
  // Multiple AI providers support
  // Soporte para múltiples proveedores de IA
  providers: ['runway', 'pika', 'sora', 'custom'];
}

interface VideoGenerationParams {
  prompt: string;           // Video description | Descripción del video
  duration: number;         // 15-120 seconds | 15-120 segundos
  style: VideoStyle;        // Visual style | Estilo visual
  aspectRatio: AspectRatio; // 16:9, 9:16, 1:1
  quality: VideoQuality;    // HD, Full HD, 4K
  aiProvider: AIProvider;   // AI service to use | Servicio IA a usar
}
```

#### 2. 🖼️ IMAGE GENERATION | GENERACIÓN DE IMÁGENES
```typescript
/**
 * AI-powered image generation
 * Generación de imágenes con IA
 */
interface ImageGenerationService {
  // Generate image
  // Generar imagen
  generateImage(params: ImageGenerationParams): Promise<ImageResult>;
  
  // Multiple AI providers
  // Múltiples proveedores de IA
  providers: ['dall-e-3', 'midjourney', 'stable-diffusion', 'custom'];
}

interface ImageGenerationParams {
  prompt: string;           // Image description | Descripción de imagen
  size: ImageSize;          // 1024x1024, 1024x1792, etc.
  style: ImageStyle;        // realistic, artistic, cartoon, etc.
  quality: ImageQuality;    // standard, hd
  aiProvider: AIProvider;   // AI service | Servicio IA
}
```

#### 3. ✍️ TEXT GENERATION | GENERACIÓN DE TEXTO
```typescript
/**
 * AI-powered text/copy generation
 * Generación de texto/copy con IA
 */
interface TextGenerationService {
  // Generate post caption
  // Generar caption para post
  generateCaption(params: CaptionParams): Promise<string>;
  
  // Generate hashtags
  // Generar hashtags
  generateHashtags(params: HashtagParams): Promise<string[]>;
  
  // Multiple AI providers
  // Múltiples proveedores de IA
  providers: ['gpt-4', 'claude', 'gemini', 'custom'];
}
```

#### 4. 🔌 UNIVERSAL AI INTEGRATION | INTEGRACIÓN UNIVERSAL DE IA
```typescript
/**
 * Connect to any AI API/Console
 * Conectar con cualquier API/Consola de IA
 */
interface UniversalAIAdapter {
  // Register new AI provider
  // Registrar nuevo proveedor de IA
  registerProvider(config: AIProviderConfig): void;
  
  // Execute request to any AI
  // Ejecutar request a cualquier IA
  execute<T>(
    provider: string,
    method: string,
    params: unknown
  ): Promise<T>;
  
  // Supported: OpenAI, Anthropic, Google, Replicate, HuggingFace, Custom
  // Soportado: OpenAI, Anthropic, Google, Replicate, HuggingFace, Custom
}

interface AIProviderConfig {
  name: string;             // Provider name | Nombre del proveedor
  baseUrl: string;          // API endpoint | Endpoint de la API
  apiKey: string;           // Authentication | Autenticación
  headers?: Record<string, string>; // Custom headers | Headers custom
  timeout?: number;         // Request timeout | Timeout del request
}
```

#### 5. 📅 SCHEDULING SYSTEM | SISTEMA DE PROGRAMACIÓN
```typescript
/**
 * Post scheduling with queue management
 * Programación de posts con gestión de cola
 */
interface SchedulingService {
  // Schedule post
  // Programar post
  schedulePost(post: ScheduledPost): Promise<ScheduleResult>;
  
  // Queue management
  // Gestión de cola
  getQueue(filters: QueueFilters): Promise<QueueItem[]>;
  
  // Bulk scheduling
  // Programación masiva
  scheduleBulk(posts: ScheduledPost[]): Promise<ScheduleResult[]>;
  
  // Cancel scheduled post
  // Cancelar post programado
  cancelScheduled(postId: string): Promise<void>;
}

interface ScheduledPost {
  id: string;
  accountId: string;        // Social media account | Cuenta de red social
  platform: Platform;       // instagram, facebook, tiktok, twitter
  content: PostContent;     // Text, images, video | Texto, imágenes, video
  scheduledTime: Date;      // When to publish | Cuándo publicar
  status: ScheduleStatus;   // pending, approved, published, failed
  priority: Priority;       // low, medium, high, urgent
}
```

#### 6. 🤖 SMART RESPONSE TEMPLATES | TEMPLATES DE RESPUESTAS INTELIGENTES
```typescript
/**
 * Context-based intelligent response system
 * Sistema de respuestas inteligentes basado en contexto
 */
interface SmartResponseService {
  // Generate contextual response
  // Generar respuesta contextual
  generateResponse(params: ResponseParams): Promise<string>;
  
  // Template management
  // Gestión de templates
  createTemplate(template: ResponseTemplate): Promise<void>;
  updateTemplate(id: string, template: Partial<ResponseTemplate>): Promise<void>;
  deleteTemplate(id: string): Promise<void>;
  
  // AI-powered suggestions
  // Sugerencias con IA
  suggestResponse(context: ResponseContext): Promise<string[]>;
}

interface ResponseTemplate {
  id: string;
  name: string;
  trigger: TriggerCondition;  // What activates this template
  template: string;            // Response template with variables
  aiEnhanced: boolean;         // Use AI to personalize
  language: Language;          // en, es, etc.
}

interface ResponseContext {
  commentText: string;         // Original comment | Comentario original
  userHistory: UserHistory;    // Past interactions | Interacciones pasadas
  sentimentScore: number;      // Sentiment analysis | Análisis de sentimiento
  intent: Intent;              // question, complaint, praise, etc.
  platform: Platform;          // Social platform | Plataforma social
}
```

#### 7. 📊 CONTROL DASHBOARD | DASHBOARD DE CONTROL
```typescript
/**
 * Centralized management dashboard
 * Dashboard centralizado de gestión
 */
interface DashboardService {
  // Overview metrics
  // Métricas generales
  getOverview(timeRange: TimeRange): Promise<DashboardOverview>;
  
  // Account management
  // Gestión de cuentas
  getAccounts(): Promise<SocialAccount[]>;
  switchAccount(accountId: string): Promise<void>;
  
  // Content calendar
  // Calendario de contenido
  getCalendar(filters: CalendarFilters): Promise<CalendarView>;
  
  // Queue management
  // Gestión de cola
  getPublishQueue(): Promise<QueueItem[]>;
  
  // Analytics
  // Analíticas
  getAnalytics(params: AnalyticsParams): Promise<AnalyticsData>;
}

interface DashboardOverview {
  totalPosts: number;          // Posts published | Posts publicados
  totalAccounts: number;       // Connected accounts | Cuentas conectadas
  queuedPosts: number;         // Posts in queue | Posts en cola
  pendingApproval: number;     // Awaiting approval | Esperando aprobación
  engagementRate: number;      // Average engagement | Engagement promedio
  followerGrowth: number;      // Follower growth | Crecimiento de seguidores
  platformBreakdown: PlatformStats[]; // Stats per platform | Stats por plataforma
}
```

#### 8. 🔐 OFFICIAL API INTEGRATION | INTEGRACIÓN CON APIs OFICIALES
```typescript
/**
 * Secure integration with official social media APIs
 * Integración segura con APIs oficiales de redes sociales
 */

// Instagram Graph API
interface InstagramAPIClient {
  // OAuth authentication
  // Autenticación OAuth
  authenticate(credentials: OAuthCredentials): Promise<AccessToken>;
  
  // Publishing
  // Publicación
  createPost(params: InstagramPostParams): Promise<PostResult>;
  createReel(params: ReelParams): Promise<PostResult>;
  createStory(params: StoryParams): Promise<PostResult>;
  
  // Engagement
  // Engagement
  getComments(mediaId: string): Promise<Comment[]>;
  replyToComment(commentId: string, text: string): Promise<void>;
  
  // Rate limit handling
  // Manejo de límites de tasa
  rateLimitStatus(): Promise<RateLimitInfo>;
}

// Facebook Graph API
interface FacebookAPIClient {
  authenticate(credentials: OAuthCredentials): Promise<AccessToken>;
  createPost(params: FacebookPostParams): Promise<PostResult>;
  getPageInsights(pageId: string): Promise<Insights>;
}

// TikTok Business API
interface TikTokAPIClient {
  authenticate(credentials: OAuthCredentials): Promise<AccessToken>;
  uploadVideo(params: TikTokVideoParams): Promise<PostResult>;
  getVideoAnalytics(videoId: string): Promise<VideoAnalytics>;
}

// Twitter API v2
interface TwitterAPIClient {
  authenticate(credentials: OAuthCredentials): Promise<AccessToken>;
  createTweet(params: TweetParams): Promise<PostResult>;
  replyToTweet(tweetId: string, text: string): Promise<void>;
}
```

#### 9. ✅ HUMAN SUPERVISION & APPROVAL | SUPERVISIÓN Y APROBACIÓN HUMANA
```typescript
/**
 * Human-in-the-loop approval system
 * Sistema de aprobación con humano en el loop
 */
interface ApprovalService {
  // Submit content for approval
  // Enviar contenido para aprobación
  submitForApproval(content: Content): Promise<ApprovalRequest>;
  
  // Get pending approvals
  // Obtener aprobaciones pendientes
  getPendingApprovals(filters: ApprovalFilters): Promise<ApprovalRequest[]>;
  
  // Approve content
  // Aprobar contenido
  approve(requestId: string, feedback?: string): Promise<void>;
  
  // Reject content
  // Rechazar contenido
  reject(requestId: string, reason: string): Promise<void>;
  
  // Request changes
  // Solicitar cambios
  requestChanges(requestId: string, changes: string): Promise<void>;
}

interface ApprovalRequest {
  id: string;
  content: Content;           // Content awaiting approval
  submittedAt: Date;          // When submitted
  submittedBy: string;        // Who/what submitted (AI or user)
  priority: Priority;         // Approval urgency
  status: ApprovalStatus;     // pending, approved, rejected, changes_requested
  reviewedAt?: Date;          // When reviewed
  reviewedBy?: string;        // Who reviewed
  feedback?: string;          // Reviewer feedback
}
```

---

## 🏛️ DDD LAYERS | CAPAS DDD

```typescript
/**
 * Domain-Driven Design architecture
 * Arquitectura de Diseño Dirigido por Dominio
 */

// 1. DOMAIN LAYER | CAPA DE DOMINIO
// Pure business logic, no dependencies
// Lógica de negocio pura, sin dependencias
domain/
├── entities/              // Business entities | Entidades de negocio
│   ├── Post.ts           // max 200 lines
│   ├── Account.ts        // max 200 lines
│   └── User.ts           // max 200 lines
├── value-objects/        // Immutable values | Valores inmutables
│   ├── Caption.ts        // max 200 lines
│   ├── Hashtag.ts        // max 200 lines
│   └── Schedule.ts       // max 200 lines
├── aggregates/           // Aggregate roots | Raíces de agregado
│   ├── ContentAggregate.ts
│   └── AccountAggregate.ts
├── repositories/         // Repository interfaces | Interfaces de repositorio
│   ├── IPostRepository.ts
│   └── IAccountRepository.ts
└── services/             // Domain services | Servicios de dominio
    ├── ContentValidator.ts
    └── ScheduleOptimizer.ts

// 2. APPLICATION LAYER | CAPA DE APLICACIÓN
// Use cases and orchestration
// Casos de uso y orquestación
application/
├── use-cases/            // Use cases | Casos de uso
│   ├── CreatePostUseCase.ts      // max 200 lines
│   ├── SchedulePostUseCase.ts    // max 200 lines
│   ├── ApproveContentUseCase.ts  // max 200 lines
│   └── GenerateContentUseCase.ts // max 200 lines
├── dto/                  // Data Transfer Objects | DTOs
│   ├── CreatePostDto.ts
│   └── SchedulePostDto.ts
└── ports/                // Input/Output ports | Puertos de entrada/salida
    ├── input/
    └── output/

// 3. INFRASTRUCTURE LAYER | CAPA DE INFRAESTRUCTURA
// External services and implementations
// Servicios externos e implementaciones
infrastructure/
├── database/             // Database implementations | Implementaciones de BD
│   ├── PostgresPostRepository.ts
│   └── RedisCache.ts
├── external-services/    // External APIs | APIs externas
│   ├── OpenAIService.ts
│   ├── InstagramAPI.ts
│   └── S3Storage.ts
└── messaging/            // Message queues | Colas de mensajes
    ├── RabbitMQPublisher.ts
    └── BullQueueService.ts

// 4. PRESENTATION LAYER | CAPA DE PRESENTACIÓN
// Controllers and API endpoints
// Controladores y endpoints de API
presentation/
├── controllers/          // REST controllers | Controladores REST
│   ├── PostController.ts        // max 200 lines
│   ├── ScheduleController.ts    // max 200 lines
│   └── ApprovalController.ts    // max 200 lines
├── middleware/           // Express middleware | Middleware de Express
│   ├── auth.middleware.ts
│   ├── validation.middleware.ts
│   └── error.middleware.ts
└── validators/           // Request validators | Validadores de request
    ├── CreatePostValidator.ts
    └── ScheduleValidator.ts
```

---

## 💎 CODE QUALITY STANDARDS | ESTÁNDARES DE CALIDAD DE CÓDIGO

### TypeScript Configuration | Configuración TypeScript
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true
  }
}
```

### Forbidden Patterns | Patrones Prohibidos
```typescript
// ❌ NEVER USE | NUNCA USAR
const data: any = fetchData();              // FORBIDDEN: 'any'
const result = data as any;                 // FORBIDDEN: 'as any'
let value: unknown;                         // FORBIDDEN without narrowing
function processData(input: any) {}         // FORBIDDEN: 'any' parameter

// ✅ ALWAYS USE | SIEMPRE USAR
interface User {
  id: string;
  name: string;
  email: string;
}

const data: User = fetchData();             // ✅ Specific type
const result = data as User;                // ✅ Specific cast (when necessary)

function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'name' in value
  );
}

function processData(input: User): void {}  // ✅ Typed parameter
```

### File Organization | Organización de Archivos
```typescript
/**
 * Every file follows this structure:
 * Cada archivo sigue esta estructura:
 * 
 * 1. Imports (grouped and sorted)
 * 2. Types and Interfaces
 * 3. Constants
 * 4. Main logic
 * 5. Exports
 */

// ✅ GOOD EXAMPLE | BUEN EJEMPLO
// file: PostService.ts (180 lines)

// 1. IMPORTS
import { Post } from '@/domain/entities/Post';
import { IPostRepository } from '@/domain/repositories/IPostRepository';
import { validateCaption } from '@/utils/validators';
import type { CreatePostDto } from '@/application/dto/CreatePostDto';

// 2. TYPES
interface PostServiceConfig {
  maxCaptionLength: number;
  allowedPlatforms: Platform[];
}

type CreatePostResult = {
  success: boolean;
  postId?: string;
  error?: string;
};

// 3. CONSTANTS
const DEFAULT_CONFIG: PostServiceConfig = {
  maxCaptionLength: 2200,
  allowedPlatforms: ['instagram', 'facebook'],
};

// 4. MAIN LOGIC
export class PostService {
  constructor(
    private readonly repository: IPostRepository,
    private readonly config: PostServiceConfig = DEFAULT_CONFIG
  ) {}

  async createPost(dto: CreatePostDto): Promise<CreatePostResult> {
    // Implementation (concise, focused)
    // Implementación (concisa, enfocada)
  }
}

// 5. EXPORTS (barrel export if needed)
export type { PostServiceConfig, CreatePostResult };
```

---

## 🔒 SECURITY REQUIREMENTS | REQUISITOS DE SEGURIDAD

```typescript
/**
 * Security is NON-NEGOTIABLE
 * La seguridad es NO NEGOCIABLE
 */

// 1. Authentication | Autenticación
interface AuthService {
  // JWT with refresh tokens
  // JWT con refresh tokens
  login(credentials: Credentials): Promise<AuthTokens>;
  refresh(refreshToken: string): Promise<AuthTokens>;
  
  // Multi-factor authentication
  // Autenticación multifactor
  enableMFA(userId: string): Promise<MFASetup>;
  verifyMFA(userId: string, code: string): Promise<boolean>;
}

// 2. Authorization | Autorización
interface AuthorizationService {
  // Role-based access control
  // Control de acceso basado en roles
  hasPermission(userId: string, resource: string, action: Action): Promise<boolean>;
  
  // Resource ownership validation
  // Validación de propiedad de recursos
  canAccessResource(userId: string, resourceId: string): Promise<boolean>;
}

// 3. Input Validation | Validación de Entrada
// ALWAYS validate and sanitize user input
// SIEMPRE validar y sanitizar entrada del usuario
import { z } from 'zod';

const CreatePostSchema = z.object({
  caption: z.string().min(1).max(2200),
  platform: z.enum(['instagram', 'facebook', 'tiktok', 'twitter']),
  scheduledTime: z.date().min(new Date()),
  mediaUrls: z.array(z.string().url()).max(10),
});

// 4. Rate Limiting | Limitación de Tasa
interface RateLimiter {
  // Protect API endpoints
  // Proteger endpoints de API
  checkLimit(userId: string, endpoint: string): Promise<boolean>;
  
  // Platform-specific rate limits
  // Límites de tasa específicos por plataforma
  checkPlatformLimit(accountId: string, platform: Platform): Promise<boolean>;
}

// 5. Secrets Management | Gestión de Secretos
// NEVER hardcode secrets | NUNCA hardcodear secretos
// ❌ const API_KEY = "sk-1234567890"; // FORBIDDEN
// ✅ const API_KEY = process.env.OPENAI_API_KEY; // REQUIRED

interface SecretsService {
  getSecret(key: string): Promise<string>;
  rotateSecret(key: string): Promise<void>;
}
```

---

## 🧪 TESTING REQUIREMENTS | REQUISITOS DE TESTING

```typescript
/**
 * All code MUST have tests
 * Todo código DEBE tener tests
 */

// 1. Unit Tests (80%+ coverage)
describe('PostService', () => {
  describe('createPost', () => {
    it('should create post with valid data', async () => {
      // Arrange
      const dto: CreatePostDto = {
        caption: 'Test post',
        platform: 'instagram',
      };
      
      // Act
      const result = await service.createPost(dto);
      
      // Assert
      expect(result.success).toBe(true);
      expect(result.postId).toBeDefined();
    });
    
    it('should reject post with invalid caption', async () => {
      const dto: CreatePostDto = {
        caption: '', // Invalid: empty
        platform: 'instagram',
      };
      
      await expect(service.createPost(dto)).rejects.toThrow();
    });
  });
});

// 2. Integration Tests
describe('Instagram API Integration', () => {
  it('should publish post to Instagram', async () => {
    // Test with real API (or mock in CI)
  });
});

// 3. E2E Tests
describe('Content Creation Flow', () => {
  it('should complete full flow: create → approve → schedule → publish', async () => {
    // Full user journey test
  });
});
```

---

## 📝 DOCUMENTATION REQUIREMENTS | REQUISITOS DE DOCUMENTACIÓN

```typescript
/**
 * Every public function/class MUST have JSDoc
 * Toda función/clase pública DEBE tener JSDoc
 */

/**
 * Creates a new social media post
 * Crea un nuevo post de redes sociales
 * 
 * @param dto - Post creation data | Datos de creación del post
 * @param options - Optional configuration | Configuración opcional
 * @returns Promise with creation result | Promise con resultado de creación
 * 
 * @throws {ValidationError} If dto is invalid | Si dto es inválido
 * @throws {AuthorizationError} If user lacks permission | Si usuario no tiene permiso
 * 
 * @example
 * ```typescript
 * const result = await postService.createPost({
 *   caption: 'Hello world!',
 *   platform: 'instagram',
 * });
 * ```
 */
async createPost(
  dto: CreatePostDto,
  options?: CreatePostOptions
): Promise<CreatePostResult> {
  // Implementation
}
```

---

## 🚀 IMPLEMENTATION PRIORITIES | PRIORIDADES DE IMPLEMENTACIÓN

### Phase 1: Foundation | Fase 1: Fundamentos (Week 1-2)
1. ✅ Project structure setup | Configuración de estructura del proyecto
2. ✅ TypeScript configuration | Configuración de TypeScript
3. ✅ Database schema | Schema de base de datos
4. ✅ Authentication system | Sistema de autenticación
5. ✅ Basic API endpoints | Endpoints básicos de API

### Phase 2: Core Features | Fase 2: Características Core (Week 3-4)
1. ✅ Text generation with AI | Generación de texto con IA
2. ✅ Image generation with AI | Generación de imagen con IA
3. ✅ Scheduling system | Sistema de programación
4. ✅ Queue management | Gestión de cola
5. ✅ Instagram API integration | Integración con API de Instagram

### Phase 3: Advanced Features | Fase 3: Características Avanzadas (Week 5-6)
1. ✅ Video generation (15-120s) | Generación de video (15-120s)
2. ✅ Smart response templates | Templates de respuestas inteligentes
3. ✅ Multi-account management | Gestión multi-cuenta
4. ✅ Dashboard UI | UI del dashboard
5. ✅ Human approval workflow | Flujo de aprobación humana

### Phase 4: Integration & Testing | Fase 4: Integración y Testing (Week 7-8)
1. ✅ All social platforms | Todas las plataformas sociales
2. ✅ Universal AI adapter | Adaptador universal de IA
3. ✅ Complete test coverage | Cobertura completa de tests
4. ✅ Performance optimization | Optimización de rendimiento
5. ✅ Production deployment | Despliegue a producción

---

## 🎯 DELIVERABLES CHECKLIST | CHECKLIST DE ENTREGABLES

### Code Quality | Calidad de Código
- [ ] No file exceeds 200 lines | Ningún archivo excede 200 líneas
- [ ] Zero 'any' types | Cero tipos 'any'
- [ ] Zero 'as any' casts | Cero casts 'as any'
- [ ] Zero 'unknown' without narrowing | Cero 'unknown' sin narrowing
- [ ] All functions typed | Todas las funciones tipadas
- [ ] All classes documented | Todas las clases documentadas
- [ ] 80%+ test coverage | 80%+ de cobertura de tests
- [ ] DDD principles followed | Principios DDD seguidos
- [ ] SOLID principles followed | Principios SOLID seguidos

### Features | Características
- [ ] Video generation (15-120s) | Generación de video (15-120s)
- [ ] Image generation | Generación de imagen
- [ ] Text generation | Generación de texto
- [ ] Universal AI integration | Integración universal de IA
- [ ] Scheduling system | Sistema de programación
- [ ] Queue management | Gestión de cola
- [ ] Smart response templates | Templates de respuestas inteligentes
- [ ] Control dashboard | Dashboard de control
- [ ] Multi-account support | Soporte multi-cuenta
- [ ] Official API integration (Meta, TikTok, Twitter) | Integración con APIs oficiales
- [ ] Human approval system | Sistema de aprobación humana

### Security | Seguridad
- [ ] Authentication implemented | Autenticación implementada
- [ ] Authorization implemented | Autorización implementada
- [ ] Input validation | Validación de entrada
- [ ] Rate limiting | Limitación de tasa
- [ ] Secrets management | Gestión de secretos
- [ ] HTTPS only | Solo HTTPS
- [ ] CORS configured | CORS configurado
- [ ] SQL injection prevention | Prevención de SQL injection

### Documentation | Documentación
- [ ] README.md complete | README.md completo
- [ ] API documentation | Documentación de API
- [ ] Architecture docs | Documentación de arquitectura
- [ ] Setup instructions | Instrucciones de configuración
- [ ] Deployment guide | Guía de despliegue

---

## 🔄 CONTINUOUS IMPROVEMENT | MEJORA CONTINUA

```typescript
/**
 * After completing any module, review:
 * Después de completar cualquier módulo, revisar:
 * 
 * 1. Can this be split further? (if > 150 lines)
 * 2. Are all types specific? (no any/unknown)
 * 3. Is logic pure and testable?
 * 4. Is documentation complete?
 * 5. Are tests comprehensive?
 * 6. Can dependencies be reduced?
 * 7. Is naming clear and consistent?
 * 8. Are DDD principles applied?
 */

// Regular refactoring checkpoints
// Puntos de control de refactorización regulares
interface RefactoringChecklist {
  fileSize: 'under_200_lines';
  typesSafety: 'strict_no_any';
  testCoverage: 'above_80_percent';
  documentation: 'complete';
  dddPrinciples: 'applied';
  solidPrinciples: 'applied';
}
```

---

## 📊 SUCCESS CRITERIA | CRITERIOS DE ÉXITO

```typescript
/**
 * Project is successful when ALL criteria are met:
 * El proyecto es exitoso cuando TODOS los criterios se cumplen:
 */

interface ProjectSuccessCriteria {
  // Architecture | Arquitectura
  maxFileSizeLines: 200;              // ✅ CRITICAL
  dddLayersImplemented: true;         // ✅ CRITICAL
  modularStructure: true;             // ✅ CRITICAL
  
  // Code Quality | Calidad de Código
  typeSafetyLevel: 'strict';          // ✅ CRITICAL (no 'any')
  testCoverage: '>80%';               // ✅ CRITICAL
  lintErrors: 0;                      // ✅ CRITICAL
  
  // Features | Características
  videoGeneration: '15-120s';         // ✅ REQUIRED
  imageGeneration: true;              // ✅ REQUIRED
  textGeneration: true;               // ✅ REQUIRED
  universalAI: true;                  // ✅ REQUIRED
  scheduling: true;                   // ✅ REQUIRED
  smartResponses: true;               // ✅ REQUIRED
  dashboard: true;                    // ✅ REQUIRED
  multiAccount: true;                 // ✅ REQUIRED
  officialAPIs: true;                 // ✅ REQUIRED
  humanApproval: true;                // ✅ REQUIRED
  
  // Performance | Rendimiento
  apiResponseTime: '<500ms';          // ✅ TARGET
  videoGenerationTime: '<5min';       // ✅ TARGET
  concurrentUsers: '>100';            // ✅ TARGET
  
  // Security | Seguridad
  authentication: 'jwt_mfa';          // ✅ CRITICAL
  authorization: 'rbac';              // ✅ CRITICAL
  inputValidation: '100%';            // ✅ CRITICAL
  secretsManagement: 'vault';         // ✅ CRITICAL
  
  // Documentation | Documentación
  apiDocs: 'complete';                // ✅ REQUIRED
  architectureDocs: 'complete';       // ✅ REQUIRED
  setupGuide: 'complete';             // ✅ REQUIRED
}
```

---

## 🎬 FINAL INSTRUCTIONS | INSTRUCCIONES FINALES

### For the Agent Building This System | Para el Agente Construyendo Este Sistema

```
🚨 CRITICAL REMINDER | RECORDATORIO CRÍTICO 🚨

1. READ these instructions COMPLETELY before starting
   LEE estas instrucciones COMPLETAMENTE antes de empezar

2. FOLLOW EVERY rule strictly - they are NON-NEGOTIABLE
   SIGUE CADA regla estrictamente - son NO NEGOCIABLES

3. NEVER exceed 200 lines per file - split when approaching limit
   NUNCA excedas 200 líneas por archivo - divide al acercarte al límite

4. ZERO tolerance for 'any' types - create specific types ALWAYS
   CERO tolerancia para tipos 'any' - crea tipos específicos SIEMPRE

5. ASK for clarification if ANY requirement is unclear
   PREGUNTA por aclaraciones si CUALQUIER requisito no está claro

6. IMPLEMENT features incrementally - test after each module
   IMPLEMENTA características incrementalmente - testea después de cada módulo

7. DOCUMENT everything - future maintainers will thank you
   DOCUMENTA todo - futuros mantenedores te lo agradecerán

8. PRIORITIZE quality over speed - "No velocity, only precision" 🐢💎
   PRIORIZA calidad sobre velocidad - "No velocidad, solo precisión" 🐢💎

Remember: This is an ENTERPRISE system that will be maintained for YEARS.
Recuerda: Este es un sistema ENTERPRISE que será mantenido por AÑOS.

Every shortcut now becomes technical debt later.
Cada atajo ahora se convierte en deuda técnica después.

Build it RIGHT, build it ONCE.
Constrúyelo BIEN, constrúyelo UNA VEZ.

🎯 You've got this! Now build something amazing! 🚀
🎯 ¡Puedes hacerlo! ¡Ahora construye algo increíble! 🚀
```

---

**END OF MASTER PROMPT**  
**FIN DEL PROMPT MAESTRO**

This prompt is your blueprint. Follow it religiously.  
Este prompt es tu blueprint. Síguelo religiosamente.

Quality is not negotiable. Excellence is the only option.  
La calidad no es negociable. La excelencia es la única opción.

🐢💎 No velocity, only precision 🐢💎
