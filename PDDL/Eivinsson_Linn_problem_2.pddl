(define (problem library-problem-2)

    (:domain library-domain)
    (:objects 
        std1 rare1 rare2         ;; The Books
        shelf workbench archive  ;; The Locations
        kit1                     ;; The Repair Kit
        j1 j2 j3 j4              ;; The Dust Jackets
    )

    (:init 
        ;; Types
        (standard-book std1) (rare-book rare1) (rare-book rare2)
        (book std1) (book rare1) (book rare2)

        (tool kit1) (kit kit1)
        (tool j1) (tool j2) (tool j3) (tool j4)
        (jacket j1) (jacket j2) (jacket j3) (jacket j4)

        (loc shelf) (loc workbench) (loc archive) (workbench workbench)
        
        ;; Initial State
        (free-hand-book) (free-hand-tool)

        (at kit1 workbench)
        (at j1 archive) (at j2 archive) (at j3 archive) (at j4 archive)
        (at std1 shelf) (at rare1 shelf) (at rare2 shelf)
    )
  
    (:goal (and
        (restored std1) (restored rare1) (restored rare2)
        (at std1 archive)
        (at rare1 shelf) (at rare2 shelf)
    ))
)
