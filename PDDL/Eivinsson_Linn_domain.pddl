(define (domain library-domain)

    (:requirements :strips)

    (:predicates (loc ?x) (workbench ?x) (at ?x ?y)
                (book ?x) (standard-book ?x) (rare-book ?x)
                (tool ?x) (kit ?x) (jacket ?x)
                (free-hand-book) (holding-book ?x)
                (free-hand-tool) (holding-tool ?x)
                (restored ?x)
    )

    ;; Action to pick up a Standard Book
    ;; Same logic as 'pick-dog': no extra tools required.
    (:action pick-standard-book
        :parameters (?b ?l)
        :precondition (and
            (standard-book ?b)
            (book ?b)
            (loc ?l)
            (at ?b ?l)
            (free-hand-book)
        )
        :effect (and
            (holding-book ?b)
            (not (at ?b ?l))
            (not (free-hand-book))
        )
    )

    ;; Action to pick up a Rare Book
    ;; LOGIC ADDED: Requires holding a jacket. The jacket is consumed (removed from hand).
    ;; Corresponds to 'pick-cat' in the Vet domain.
    (:action pick-rare-book
       :parameters (?b ?l ?j)
       :precondition (and
            (rare-book ?b)
            (book ?b)
            (loc ?l)
            (at ?b ?l)
            (free-hand-book)
            (holding-tool ?j)
            (jacket ?j)
       )
       :effect (and
            (holding-book ?b)
            (not (at ?b ?l))
            (not (free-hand-book))

            ;; Jacket is used to wrap the book and is removed from hand
            (free-hand-tool)
            (not (holding-tool ?j))
       )
    )

    ;; Action to drop a book
    (:action drop-book
        :parameters (?b ?l)
        :precondition (and
            (holding-book ?b)
            (book ?b)
            (loc ?l)
        )
        :effect (and
            (at ?b ?l)
            (free-hand-book)
            (not (holding-book ?b))
        )
    )

    ;; Action to pick up a tool (Jacket or Kit)
    (:action pick-tool
        :parameters (?t ?l)
        :precondition (and
            (tool ?t)
            (loc ?l)
            (at ?t ?l)
            (free-hand-tool)
        )
        :effect (and
            (holding-tool ?t)
            (not (at ?t ?l))
            (not (free-hand-tool))
        )
    )

    ;; Action to drop a tool
    (:action drop-tool
        :parameters (?t ?l)
        :precondition (and
            (holding-tool ?t)
            (tool ?t)
            (loc ?l)
        )
        :effect (and
            (at ?t ?l)
            (free-hand-tool)
            (not (holding-tool ?t))
        )
    )

    ;; Action to restore a book
    ;; LOGIC ADDED: Sets the book to 'restored'.
    ;; Corresponds to 'use-syringe' in the Vet domain.
    (:action restore-book
        :parameters (?b ?w ?k)
        :precondition (and
            (book ?b)
            (loc ?w)
            (workbench ?w)
            (at ?b ?w)
            (holding-tool ?k)
            (kit ?k)
        )
        :effect (and
            (restored ?b)
        )
    )
)
