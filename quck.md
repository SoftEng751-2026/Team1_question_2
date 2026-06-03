Q1: "Why did you split by rows instead of using 2D blocks/tiles?"
Answer: "Row-splitting is simpler — each thread gets contiguous rows, and the neighbor access pattern only needs the row above and below, which is adjacent in memory. With 2D blocks, boundaries are more complex — each block needs neighbors from all four sides, and you have more communication overhead. Row-splitting also maps naturally to flat 1D arrays where rows are laid out sequentially. The downside is less cache reuse on the row boundaries, but our padded stride prevents false sharing, so the simplicity wins."
---
Q2: "Your Java efficiency is >100%. Isn't that impossible?"
Answer: "It's not impossible — it just means the baseline isn't fair. Our speedup formula compares the optimized parallel version against the sequential implementation at 1 thread. But the sequential version uses jagged int[][] arrays, while the optimized version uses flat int[] with padding. Even at 1 thread with zero parallelism, the optimized version is 2.3x faster just from better memory layout. So the 11x speedup bundles ~2.3x from memory optimization and ~4.9x from actual parallelism. True parallel efficiency on 8 threads is about 61%. We show this to be transparent, not to inflate numbers."
---
Q3: "Why is Java slower than C++ even after JIT compilation?"
Answer: "Three main reasons. First, C++ was compiled with -O3 which enables aggressive loop unrolling, auto-vectorization with SIMD instructions, and whole-program inlining — the JIT can't spend that much time optimizing at runtime. Second, Java has runtime overhead the JIT can't eliminate: bounds checks on every array access, null checks, and object header overhead. Third, C++ uses raw pointers — grid[i * stride + j] compiles to one mov instruction — while Java's int[] is an object with header and length metadata. The JIT does a good job, but it can't erase the abstraction cost entirely."
---
Q4: "Why didn't you use a ghost cell border to avoid boundary checks?"
Answer: "We considered it, but for this benchmark it wasn't worth it. Adding a border of dead cells around the grid means allocating a (rows+2) x (cols+2) grid and always having valid neighbors at the edges. This eliminates all the hasLeft/hasRight/hasUp/hasDown checks in the inner loop. However, with our approach of explicit conditionals, the boundary checks are cheap — they're booleans evaluated once per row, not per cell. For the 2048² grid, boundary cells are only ~0.4% of total cells, so the optimization would save less than 0.5% of total work. Not worth the extra allocation complexity."
---
Q5: "Did you verify correctness — does your parallel output match the sequential output?"
Answer: "That's a good point and something we should have done more rigorously. We verified visually that grids converge to expected Game of Life patterns, but we didn't add automated correctness tests comparing parallel output against sequential output for the same seed. Since each thread writes to disjoint row ranges and we use double buffering, there's no data race — the parallel version should be bit-identical to sequential. In hindsight, adding a diff check per iteration would have been a cleaner verification. This is something we'd add in a future iteration."
---
Q6: "Why static scheduling in OpenMP instead of dynamic or guided?"
Answer: "Game of Life is perfectly uniform — every row does exactly the same amount of work. Static scheduling divides rows into equal chunks once, with zero runtime overhead. Dynamic and guided scheduling add overhead from a work queue that threads check at runtime — useful when work per iteration varies (e.g., sparse matrix computations) but wasteful here. For our workload, static is the optimal choice."
---
Q7: "What happens if you go beyond 8 threads?"
Answer: "We'd expect diminishing returns. On this CPU, 8 threads likely matches the physical core count. Beyond that, you get hyperthreading which might give ~10-20% more throughput, or you start oversubscribing which hurts. The bigger limit is memory bandwidth — at 8 threads, C++ throughput on 2048² dropped 10% compared to 512², signaling we're approaching the DRAM bandwidth ceiling. More threads would increase contention for that fixed bandwidth without much speedup gain."
---
Q8: "Why not use C++ std::thread or Java Thread directly instead of OpenMP/ForkJoin?"
Answer: "OpenMP is the standard for HPC stencil codes — it's one pragma, handles thread creation and barriers automatically, and the compiler optimizes the loop distribution. Writing raw std::thread would mean manually partitioning rows, joining threads, and reimplementing barriers — more code, more bugs, no performance gain.
On the Java side, raw threads would work but ForkJoin gives us automatic work-stealing and a well-tested thread pool. Writing our own thread pool with manual work distribution would be error-prone and likely perform worse than the JDK's optimized implementation."
---
Q9: "Does your C++ sequential version use -O3 too, and if so, why is it still slower than optimized 1T?"
Answer: "Yes, both C++ versions compile with -O3. The difference is entirely memory layout. The sequential version uses vector<vector<int>> — nested vectors with separate heap allocations per row. -O3 can unroll loops and inline functions, but it can't fix the fact that each row is a random memory address. Every row transition is a cache miss. The optimized version uses a flat int* with padding — one contiguous allocation, aligned to 64 bytes. This is a level of optimization the compiler can't automatically do for you; it requires changing the data structure. That's exactly the lesson: no compiler flag can fix a bad memory layout."
---
Q10: "How do these results generalize to other stencil computations?"
Answer: "The memory optimizations — flat arrays, padding, alignment — apply to any stencil. The parallelization strategy depends on the stencil radius. For a 5-point heat diffusion stencil (neighbors only up/down/left/right), row-splitting works identically. For wider stencils that need neighbors further away, you'd need overlapping row chunks (halo exchange) or 2D tiling. The cache-line padding lesson applies universally to any shared-memory parallel code that partitions data structures — false sharing kills performance regardless of the computation."
---
Q11: "What would you do differently if you had more time?"
Answer: "Three things. First, add automated correctness verification — compare parallel output bit-by-bit against sequential output for every test case. Second, add a ghost cell border to measure whether eliminating boundary checks in the inner loop makes a measurable difference. Third, profile with perf or a similar tool to understand exactly where cycles are spent — is it ALU-bound, L1-miss-bound, or DRAM-bound at different thread counts? That would confirm our bandwidth saturation hypothesis."
---
Q12: "Your C++ 8-thread times sometimes vary significantly between runs. Why?"
Answer: "At 8 threads, we're competing with the operating system for resources. Background processes, OS scheduling, interrupt handling, and thermal throttling all cause variance. On a shared university machine, other users' processes also contend for cache and memory bandwidth. That's why we run 5 repetitions and take the mean — it smooths out these transient effects. The standard deviation we report in the efficiency and speedup plots captures this variance."
---
Q13: "Why does the Java optimized version sometimes beat ideal speedup but C++ doesn't?"
Answer: "Because the Java baseline is worse relative to the optimized version. Java's sequential int[][] has terrible cache behavior because of the JVM's object layout — Java jagged arrays have object headers per row, extra indirection, and no control over allocation placement. When we switch to a flat int[], Java gains more proportionally than C++ does from its flat int*. So the combined speedup (memory + threads) is larger for Java. The C++ sequential is also slower than optimized 1T, but the gap is smaller because the C++ compiler partially mitigates nested vector overhead. The true parallel speedup — optimized 1T vs 8T — is similar for both: ~5x."
---
Q14: "Why did you choose those specific grid sizes?"
Answer: "Each step up is 2x in each dimension = 4x the cells. We scaled iterations inversely so total work roughly doubles each step (26M → 52M → 105M cells). This lets us see how each implementation scales with problem size. The smallest at 512² is small enough to mostly fit in L2/L3 cache. The largest at 2048² exceeds cache sizes — 2048² ints = 16 MB for the grid alone — so it forces DRAM traffic, which stresses the memory subsystem. That's why we see the throughput drop at 8 threads only on 2048² — it's memory bandwidth bound."
---
Q15: "How do you know the 3 warm-up iterations in Java were enough?"
Answer: "We don't for certain, but we can infer from the data. The standard deviation across 5 runs is small (typically 2-5% of the mean), and the sequential times don't drift downward across runs. If the JIT were still compiling during timed iterations, we'd see higher variance and a downward trend. The consistent numbers suggest steady state was reached. A more rigorous approach would be to measure iteration-by-iteration times and identify the knee where times stabilize — then set warm-up count past that point. For a simple computation like this, 3 iterations is generally sufficient to trigger compilation for hot methods."
---
Bonus questions they might ask about your specific implementation:
Question	Key answer point
"Why 16 ints per cache line in Java? Isn't a cache line 64 bytes?"	"16 ints × 4 bytes = 64 bytes. Same thing."
"Why is TILE_ROWS=64 in the ForkJoin?"	"Small enough for load balancing, large enough that task creation overhead is negligible relative to compute work."
"Did you pin threads to cores?"	"No — we relied on the OS scheduler. Pinning via taskset or omp_proc_bind could improve consistency but we wanted real-world behavior."
"How does the __restrict__ keyword in C++ help?"	"Tells the compiler the cur and nxt pointers don't alias — they point to disjoint memory. Without it, GCC might reload on every iteration fearing overlap. With __restrict__, it can keep values in registers."
---



1. Memory Architecture & Hardware

Q: "You emphasized flattening the 2D grid into a 1D array. Why is that strictly better than an array of arrays?"

    The Trap: They want to make sure you know the difference between logical layout and physical hardware behavior.

    Key Points to Hit:

        Spatial Locality: A 1D array guarantees a single, contiguous block of memory.

        Cache Lines: It allows the CPU to fetch 64-byte chunks (16 integers) at once. A contiguous array gives you 1 cache miss followed by 15 "free" cache hits.

        TLB Thrashing: Jagged arrays (arrays of pointers) scatter rows across random 4KB memory pages, overwhelming the Translation Lookaside Buffer (TLB) and causing constant 50-cycle page walks.

Q: "Why did you split the parallel workload by rows instead of by columns?"

    The Trap: Testing your understanding of how 2D data sits inside 1D memory.

    Key Points to Hit:

        In a flattened array, rows are contiguous in physical memory, but columns are spaced out by the width of the grid.

        Splitting by columns destroys the hardware prefetcher's ability to guess the next memory address and guarantees massive False Sharing down the vertical boundaries, as threads would constantly cross paths inside the same cache lines.

2. False Sharing & Optimizations

Q: "You implemented cache line padding. Can you explain exactly what False Sharing is and why padding solves it?"

    The Trap: They are looking for the acronym "MESI" and the concept of cache coherency.

    Key Points to Hit:

        False sharing occurs when two independent threads modify different variables that happen to live inside the exact same 64-byte cache line.

        The MESI protocol forces the CPU cores to constantly invalidate and "bounce" the cache line back and forth across the L3 cache, causing hundreds of wasted clock cycles.

        Padding stretches every row to be a perfect multiple of 64 bytes, ensuring Thread A and Thread B are physically isolated in their own cache lines.

Q: "If your rows are already padded, why did you also need _aligned_malloc in C++?"

    The Trap: Testing if you know the difference between the size of a block and the placement of a block.

    Key Points to Hit:

        Padding only guarantees the length of the row.

        Standard malloc might start the array halfway through a cache line. If the starting address is offset, the perfectly padded rows will straddle the cache line boundaries, pushing the end of Row 0 and the start of Row 1 back into the same physical box, bringing False Sharing back. Alignment guarantees the array starts perfectly at byte 0 of a cache line.

3. Concurrency Models: Java vs. C++

Q: "Your C++ OpenMP implementation using static scheduling was much faster. Why didn't you just use static thread scheduling in Java instead of ForkJoin?"

    The Trap: They want to see if you understand the reality of running code inside a Virtual Machine.

    Key Points to Hit:

        C++ runs directly on the metal (a "perfect vacuum"). Static scheduling works beautifully because the threads are rarely interrupted.

        Java runs inside the JVM, which introduces JVM Jitter (Garbage Collection pauses, JIT compilation).

        If a static Java thread gets frozen by the Garbage Collector, the synchronization barrier forces all other threads to sit idle. ForkJoin’s work-stealing acts as an insurance policy—idle threads steal the frozen thread's work, keeping CPU utilization high despite the chaotic JVM environment.

Q: "Besides the ForkJoin overhead, what else constitutes the 'Safety Tax' that makes your Java implementation slower than C++?"

    Key Points to Hit:

        Bounds Checking: The JVM quietly injects array bounds checks on every memory access.

        Lack of __restrict__: C++ allows you to promise the compiler that memory arrays don't overlap, which unlocks aggressive SIMD (Single Instruction, Multiple Data) vectorization. Java lacks this, preventing the CPU from processing multiple cells in a single hardware instruction.

        Object Headers: Java arrays have hidden object headers, making absolute cache-line alignment nearly impossible.

4. Data Analysis & Hardware Limits

Q: "Looking at your results, throughput stops scaling perfectly after 6 threads. Why?"

    The Trap: Checking if you know the specs of your test machine (Ryzen 5 7600) and the reality of Hyperthreading.

    Key Points to Hit:

        The CPU only has 6 physical cores.

        Scaling from 1 to 6 threads provides near-linear gains because fresh physical hardware is being utilized.

        Threads 7 through 12 are Logical Threads (SMT/Hyperthreading). They do not double performance; they only hide memory latency by keeping the core busy during cache misses. Pushing beyond 12 threads would cause oversubscription and severe context-switching penalties.

Q: "In your graph, there is a massive error bar and a huge performance drop for the C++ sequential 2048x2048 4T run. How do you explain this anomaly?"

    The Trap: Every professor looks for the weirdest data point to see if you will admit to environmental noise or if you will try to invent a fake technical reason.

    Key Points to Hit:

        Acknowledge it as an anomaly. Since the 1T, 2T, and 8T sequential runs are identical, the 4T sequential run should be flat.

        Attribute it to environmental noise—an OS interrupt, a sudden thermal throttle, or a background process (like an antivirus scan or Windows Update) that hijacked the CPU during that specific benchmark iteration, skewing the average.