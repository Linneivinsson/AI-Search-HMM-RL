(define (problem library-problem)

    (:domain library-domain)
    (:objects 
        b-std b-rare       ;; The Books
        bench shelf        ;; The Locations
        k                  ;; The Repair Kit
        j1 j2              ;; The Dust Jackets
    )

    (:init 
        ;; Types
        (standard-book b-std) (rare-book b-rare) (book b-std) (book b-rare)
        (tool k) (tool j1) (tool j2) (kit k) (jacket j1) (jacket j2)
        (loc shelf) (loc bench) (workbench bench)
        
        ;; Initial State
        (free-hand-book) (free-hand-tool)
        (at k shelf) (at j1 shelf) (at j2 shelf) 
        (at b-std shelf) (at b-rare shelf)
    )
  
    (:goal (and (restored b-std) (restored b-rare) (at b-std shelf) (at b-rare shelf)))
)
