package ssti;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.lang.reflect.Method;
import java.lang.reflect.Constructor;


public class TemplateWorker {
    private static final int DEFAULT_WORKER_THREADS = Runtime.getRuntime().availableProcessors() * 2;
    private static final long EXECUTION_TIMEOUT = 10; // seconds
    
    private final ExecutorService workerExecutor;
    private final EngineLoader engineLoader;
    private final AtomicLong executionCounter;
    
    public TemplateWorker(EngineLoader engineLoader) {
        this(engineLoader, DEFAULT_WORKER_THREADS);
    }
    
    public TemplateWorker(EngineLoader engineLoader, int workerThreads) {
        this.engineLoader = engineLoader;
        this.executionCounter = new AtomicLong(0);
        
        this.workerExecutor = new ThreadPoolExecutor(
            workerThreads,
            workerThreads,
            60L,
            TimeUnit.SECONDS,
            new LinkedBlockingQueue<>(),
            new ThreadFactory() {
                private final AtomicLong threadNumber = new AtomicLong(1);
                @Override
                public Thread newThread(Runnable r) {
                    Thread t = new Thread(r, "TemplateWorker-" + threadNumber.getAndIncrement());
                    t.setDaemon(true);
                    return t;
                }
            }
        );
    }
    
    /**
     * Execute template processing asynchronously
     */
    public CompletableFuture<String> processTemplateAsync(String engineName, String template, Map<String, Object> context) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                return processTemplateSync(engineName, template, context);
            } catch (Exception e) {
                throw new RuntimeException("Template processing failed", e);
            }
        }, workerExecutor);
    }
    
    /**
     * Execute multiple templates concurrently
     */
    public CompletableFuture<Map<String, String>> processTemplatesAsync(Map<String, TemplateRequest> requests) {
        List<CompletableFuture<TemplateResult>> futures = new ArrayList<>();
        
        for (Map.Entry<String, TemplateRequest> entry : requests.entrySet()) {
            String requestId = entry.getKey();
            TemplateRequest request = entry.getValue();
            
            CompletableFuture<TemplateResult> future = processTemplateAsync(
                request.getEngineName(),
                request.getTemplate(),
                request.getContext()
            ).thenApply(result -> new TemplateResult(requestId, result, null))
             .exceptionally(throwable -> new TemplateResult(requestId, null, throwable.getMessage()));
            
            futures.add(future);
        }
        
        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
            .thenApply(v -> {
                Map<String, String> results = new HashMap<>();
                for (CompletableFuture<TemplateResult> future : futures) {
                    try {
                        TemplateResult result = future.get();
                        if (result.getError() != null) {
                            results.put(result.getRequestId(), "ERROR: " + result.getError());
                        } else {
                            results.put(result.getRequestId(), result.getResult());
                        }
                    } catch (Exception e) {
                        // This shouldn't happen as we handle exceptions above
                        System.err.println("Unexpected error: " + e.getMessage());
                    }
                }
                return results;
            });
    }
    
    /**
     * Synchronous template processing
     */
    private String processTemplateSync(String engineName, String template, Map<String, Object> context) throws Exception {
        long startTime = System.currentTimeMillis();
        long executionId = executionCounter.incrementAndGet();
        
        System.out.println("Processing template #" + executionId + " with engine: " + engineName + 
                          " (Thread: " + Thread.currentThread().getName() + ")");
        
        try {
            Object engine = engineLoader.getEngine(engineName);
            String result = executeTemplate(engineName, engine, template, context);
            
            long duration = System.currentTimeMillis() - startTime;
            System.out.println("Template #" + executionId + " processed successfully in " + duration + "ms");
            
            return result;
            
        } catch (Exception e) {
            long duration = System.currentTimeMillis() - startTime;
            System.err.println("Template #" + executionId + " failed after " + duration + "ms: " + e.getMessage());
            throw e;
        }
    }
    
    /**
     * Execute template with specific engine
     */
    private String executeTemplate(String engineName, Object engine, String template, Map<String, Object> context) throws Exception {
        switch (engineName.toLowerCase()) {
            case "velocity":
                return executeVelocityTemplate(engine, template, context);
            case "freemarker":
                return executeFreemarkerTemplate(engine, template, context);
            case "thymeleaf":
                return executeThymeleafTemplate(engine, template, context);
            case "mustache":
                return executeMustacheTemplate(engine, template, context);
            case "handlebars":
                return executeHandlebarsTemplate(engine, template, context);
            case "pebble":
                return executePebbleTemplate(engine, template, context);
            default:
                throw new IllegalArgumentException("Unsupported engine: " + engineName);
        }
    }
    
    private String executeVelocityTemplate(Object engine, String template, Map<String, Object> context) throws Exception {
        // Velocity implementation
        Class<?> velocityContextClass = Class.forName("org.apache.velocity.VelocityContext");
        Object velocityContext = velocityContextClass.getDeclaredConstructor(Map.class).newInstance(context);
        
        Method evaluateMethod = engine.getClass().getMethod("evaluate", 
            velocityContextClass, java.io.Writer.class, String.class, String.class);
        
        java.io.StringWriter writer = new java.io.StringWriter();
        evaluateMethod.invoke(engine, velocityContext, writer, "template", template);
        
        return writer.toString();
    }
    
    private String executeFreemarkerTemplate(Object config, String template, Map<String, Object> context) throws Exception {
        // Freemarker implementation
        Class<?> templateClass = Class.forName("freemarker.template.Template");
        Constructor<?> templateConstructor = templateClass.getConstructor(String.class, String.class, Object.class);
        Object templateObj = templateConstructor.newInstance("template", template, config);
        
        Method processMethod = templateClass.getMethod("process", Object.class, java.io.Writer.class);
        java.io.StringWriter writer = new java.io.StringWriter();
        processMethod.invoke(templateObj, context, writer);
        
        return writer.toString();
    }
    
    private String executeThymeleafTemplate(Object engine, String template, Map<String, Object> context) throws Exception {
        // Thymeleaf implementation
        Class<?> contextClass = Class.forName("org.thymeleaf.context.Context");
        Object thymeleafContext = contextClass.getDeclaredConstructor().newInstance();
        
        Method setVariablesMethod = contextClass.getMethod("setVariables", Map.class);
        setVariablesMethod.invoke(thymeleafContext, context);
        
        Method processMethod = engine.getClass().getMethod("process", String.class, contextClass);
        return (String) processMethod.invoke(engine, template, thymeleafContext);
    }
    
    private String executeMustacheTemplate(Object factory, String template, Map<String, Object> context) throws Exception {
        // Mustache implementation
        Method compileMethod = factory.getClass().getMethod("compile", String.class, String.class);
        Object mustache = compileMethod.invoke(factory, template, "template");
        
        Method executeMethod = mustache.getClass().getMethod("execute", java.io.Writer.class, Object.class);
        java.io.StringWriter writer = new java.io.StringWriter();
        executeMethod.invoke(mustache, writer, context);
        
        return writer.toString();
    }
    
    private String executeHandlebarsTemplate(Object handlebars, String template, Map<String, Object> context) throws Exception {
        // Handlebars implementation
        Method compileInlineMethod = handlebars.getClass().getMethod("compileInline", String.class);
        Object compiledTemplate = compileInlineMethod.invoke(handlebars, template);
        
        Method applyMethod = compiledTemplate.getClass().getMethod("apply", Object.class);
        return (String) applyMethod.invoke(compiledTemplate, context);
    }
    
    private String executePebbleTemplate(Object engine, String template, Map<String, Object> context) throws Exception {
        // Pebble implementation
        Method getLiteralTemplateMethod = engine.getClass().getMethod("getLiteralTemplate", String.class);
        Object pebbleTemplate = getLiteralTemplateMethod.invoke(engine, template);
        
        Method evaluateMethod = pebbleTemplate.getClass().getMethod("evaluate", java.io.Writer.class, Map.class);
        java.io.StringWriter writer = new java.io.StringWriter();
        evaluateMethod.invoke(pebbleTemplate, writer, context);
        
        return writer.toString();
    }
    
    /**
     * Get worker statistics
     */
    public Map<String, Object> getStatistics() {
        ThreadPoolExecutor executor = (ThreadPoolExecutor) workerExecutor;
        Map<String, Object> stats = new HashMap<>();
        stats.put("totalExecutions", executionCounter.get());
        stats.put("workerThreads", executor.getCorePoolSize());
        stats.put("activeWorkers", executor.getActiveCount());
        stats.put("completedTasks", executor.getCompletedTaskCount());
        stats.put("queueSize", executor.getQueue().size());
        return stats;
    }
    
    /**
     * Shutdown the worker threads
     */
    public void shutdown() {
        workerExecutor.shutdown();
        try {
            if (!workerExecutor.awaitTermination(30, TimeUnit.SECONDS)) {
                workerExecutor.shutdownNow();
            }
        } catch (InterruptedException e) {
            workerExecutor.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
    
    // Helper classes
    public static class TemplateRequest {
        private final String engineName;
        private final String template;
        private final Map<String, Object> context;
        
        public TemplateRequest(String engineName, String template, Map<String, Object> context) {
            this.engineName = engineName;
            this.template = template;
            this.context = context;
        }
        
        public String getEngineName() { return engineName; }
        public String getTemplate() { return template; }
        public Map<String, Object> getContext() { return context; }
    }
    
    private static class TemplateResult {
        private final String requestId;
        private final String result;
        private final String error;
        
        public TemplateResult(String requestId, String result, String error) {
            this.requestId = requestId;
            this.result = result;
            this.error = error;
        }
        
        public String getRequestId() { return requestId; }
        public String getResult() { return result; }
        public String getError() { return error; }
    }
}
