package ssti;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.lang.reflect.Method;
import java.lang.reflect.Constructor;

public class EngineLoader {
    private static final int DEFAULT_THREAD_POOL_SIZE = Runtime.getRuntime().availableProcessors();
    private static final int MAX_THREAD_POOL_SIZE = 20;
    private static final long THREAD_TIMEOUT = 30; // seconds
    
    private final ExecutorService executorService;
    private final Map<String, Object> loadedEngines;
    private final Map<String, CompletableFuture<Object>> loadingFutures;
    private final AtomicInteger loadCounter;
    
    // Supported template engines
    private static final Map<String, String> ENGINE_CLASSES = new HashMap<>();
    static {
        ENGINE_CLASSES.put("velocity", "org.apache.velocity.app.VelocityEngine");
        ENGINE_CLASSES.put("freemarker", "freemarker.template.Configuration");
        ENGINE_CLASSES.put("thymeleaf", "org.thymeleaf.TemplateEngine");
        ENGINE_CLASSES.put("mustache", "com.github.mustachejava.DefaultMustacheFactory");
        ENGINE_CLASSES.put("handlebars", "com.github.jknack.handlebars.Handlebars");
        ENGINE_CLASSES.put("pebble", "com.mitchellbosecke.pebble.PebbleEngine");
    }
    
    public EngineLoader() {
        this(DEFAULT_THREAD_POOL_SIZE);
    }
    
    public EngineLoader(int threadPoolSize) {
        int poolSize = Math.min(Math.max(threadPoolSize, 1), MAX_THREAD_POOL_SIZE);
        
        this.executorService = new ThreadPoolExecutor(
            poolSize,
            poolSize,
            THREAD_TIMEOUT,
            TimeUnit.SECONDS,
            new LinkedBlockingQueue<>(),
            new ThreadFactory() {
                private final AtomicInteger threadNumber = new AtomicInteger(1);
                @Override
                public Thread newThread(Runnable r) {
                    Thread t = new Thread(r, "EngineLoader-" + threadNumber.getAndIncrement());
                    t.setDaemon(true);
                    return t;
                }
            }
        );
        
        this.loadedEngines = new ConcurrentHashMap<>();
        this.loadingFutures = new ConcurrentHashMap<>();
        this.loadCounter = new AtomicInteger(0);
    }
    
    /**
     * Load a template engine asynchronously
     */
    public CompletableFuture<Object> loadEngineAsync(String engineName) {
        return loadingFutures.computeIfAbsent(engineName, name -> {
            return CompletableFuture.supplyAsync(() -> {
                try {
                    return loadEngineSync(name);
                } catch (Exception e) {
                    throw new RuntimeException("Failed to load engine: " + name, e);
                }
            }, executorService);
        });
    }
    
    /**
     * Load multiple engines concurrently
     */
    public CompletableFuture<Map<String, Object>> loadEnginesAsync(String... engineNames) {
        List<CompletableFuture<Object>> futures = new ArrayList<>();
        Map<String, String> nameMapping = new HashMap<>();
        
        for (String engineName : engineNames) {
            futures.add(loadEngineAsync(engineName));
            nameMapping.put(engineName, engineName);
        }
        
        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
            .thenApply(v -> {
                Map<String, Object> results = new HashMap<>();
                for (String engineName : engineNames) {
                    try {
                        Object engine = loadingFutures.get(engineName).get();
                        results.put(engineName, engine);
                    } catch (Exception e) {
                        System.err.println("Failed to load engine " + engineName + ": " + e.getMessage());
                    }
                }
                return results;
            });
    }
    
    /**
     * Load all available engines concurrently
     */
    public CompletableFuture<Map<String, Object>> loadAllEnginesAsync() {
        return loadEnginesAsync(ENGINE_CLASSES.keySet().toArray(new String[0]));
    }
    
    /**
     * Synchronous engine loading (used internally)
     */
    private Object loadEngineSync(String engineName) throws Exception {
        // Check if already loaded
        Object cachedEngine = loadedEngines.get(engineName);
        if (cachedEngine != null) {
            return cachedEngine;
        }
        
        String className = ENGINE_CLASSES.get(engineName.toLowerCase());
        if (className == null) {
            throw new IllegalArgumentException("Unsupported engine: " + engineName);
        }
        
        System.out.println("Loading engine: " + engineName + " (Thread: " + Thread.currentThread().getName() + ")");
        
        try {
            Class<?> engineClass = Class.forName(className);
            Object engine = createEngineInstance(engineName, engineClass);
            
            loadedEngines.put(engineName, engine);
            loadCounter.incrementAndGet();
            
            System.out.println("Successfully loaded engine: " + engineName);
            return engine;
            
        } catch (ClassNotFoundException e) {
            throw new Exception("Engine class not found: " + className + ". Make sure the dependency is included.", e);
        } catch (Exception e) {
            throw new Exception("Failed to instantiate engine: " + engineName, e);
        }
    }
    
    /**
     * Create engine instance with proper configuration
     */
    private Object createEngineInstance(String engineName, Class<?> engineClass) throws Exception {
        switch (engineName.toLowerCase()) {
            case "velocity":
                return createVelocityEngine(engineClass);
            case "freemarker":
                return createFreemarkerEngine(engineClass);
            case "thymeleaf":
                return createThymeleafEngine(engineClass);
            case "mustache":
                return createMustacheEngine(engineClass);
            case "handlebars":
                return createHandlebarsEngine(engineClass);
            case "pebble":
                return createPebbleEngine(engineClass);
            default:
                // Default constructor
                return engineClass.getDeclaredConstructor().newInstance();
        }
    }
    
    private Object createVelocityEngine(Class<?> engineClass) throws Exception {
        Object engine = engineClass.getDeclaredConstructor().newInstance();
        Method initMethod = engineClass.getMethod("init");
        initMethod.invoke(engine);
        return engine;
    }
    
    private Object createFreemarkerEngine(Class<?> engineClass) throws Exception {
        Constructor<?> constructor = engineClass.getConstructor();
        Object config = constructor.newInstance();
        
        // Set template loader
        Method setTemplateLoaderMethod = engineClass.getMethod("setClassForTemplateLoading", Class.class, String.class);
        setTemplateLoaderMethod.invoke(config, this.getClass(), "/templates");
        
        return config;
    }
    
    private Object createThymeleafEngine(Class<?> engineClass) throws Exception {
        return engineClass.getDeclaredConstructor().newInstance();
    }
    
    private Object createMustacheEngine(Class<?> engineClass) throws Exception {
        return engineClass.getDeclaredConstructor().newInstance();
    }
    
    private Object createHandlebarsEngine(Class<?> engineClass) throws Exception {
        return engineClass.getDeclaredConstructor().newInstance();
    }
    
    private Object createPebbleEngine(Class<?> engineClass) throws Exception {
        Method builderMethod = engineClass.getMethod("newBuilder");
        Object builder = builderMethod.invoke(null);
        Method buildMethod = builder.getClass().getMethod("build");
        return buildMethod.invoke(builder);
    }
    
    /**
     * Get a loaded engine (blocking if still loading)
     */
    public Object getEngine(String engineName) throws Exception {
        CompletableFuture<Object> future = loadingFutures.get(engineName);
        if (future != null) {
            return future.get(THREAD_TIMEOUT, TimeUnit.SECONDS);
        }
        
        Object engine = loadedEngines.get(engineName);
        if (engine == null) {
            throw new IllegalStateException("Engine not loaded: " + engineName);
        }
        return engine;
    }
    
    /**
     * Check if an engine is loaded
     */
    public boolean isEngineLoaded(String engineName) {
        return loadedEngines.containsKey(engineName);
    }
    
    /**
     * Get loading status
     */
    public Map<String, String> getLoadingStatus() {
        Map<String, String> status = new HashMap<>();
        
        for (String engineName : ENGINE_CLASSES.keySet()) {
            if (loadedEngines.containsKey(engineName)) {
                status.put(engineName, "LOADED");
            } else if (loadingFutures.containsKey(engineName)) {
                CompletableFuture<Object> future = loadingFutures.get(engineName);
                if (future.isDone()) {
                    if (future.isCompletedExceptionally()) {
                        status.put(engineName, "FAILED");
                    } else {
                        status.put(engineName, "LOADED");
                    }
                } else {
                    status.put(engineName, "LOADING");
                }
            } else {
                status.put(engineName, "NOT_STARTED");
            }
        }
        
        return status;
    }
    
    /**
     * Get statistics
     */
    public Map<String, Object> getStatistics() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("totalEngines", ENGINE_CLASSES.size());
        stats.put("loadedEngines", loadedEngines.size());
        stats.put("loadingEngines", loadingFutures.size() - loadedEngines.size());
        stats.put("threadPoolSize", ((ThreadPoolExecutor) executorService).getCorePoolSize());
        stats.put("activeThreads", ((ThreadPoolExecutor) executorService).getActiveCount());
        stats.put("completedTasks", ((ThreadPoolExecutor) executorService).getCompletedTaskCount());
        return stats;
    }
    
    /**
     * Shutdown the thread pool
     */
    public void shutdown() {
        executorService.shutdown();
        try {
            if (!executorService.awaitTermination(THREAD_TIMEOUT, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
        } catch (InterruptedException e) {
            executorService.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
    
    /**
     * Get available engine names
     */
    public Set<String> getAvailableEngines() {
        return new HashSet<>(ENGINE_CLASSES.keySet());
    }
}
