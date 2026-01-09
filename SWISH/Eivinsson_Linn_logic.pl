%%  iss_crew(-Solution)
%   @param  Solution is a list of crew members that satisfy all constraints.

/* 4 Astronauts Logical Puzzle:
*
* The constants:
* Astronauts: alex, sam, jo, pat
* Roles: commander, pilot, specialist, engineer
* Modules: command_node, lab_node
* Foods: beef, tofu, pasta, curry
* Drinks: water, tea, coffee, juice
*
* We define that:
* Two astronauts are crew_mates if they are in the same module.
*
* And we know the following facts:
* F1- Jo is in the lab_node.
* F2- Alex drinks water.
* F3- Pat is the pilot.
* F4- The astronaut who eats tofu drinks tea.
* F5- Sam and Pat are crew_mates.
* F6- Exactly two astronauts are in each module.
* F7- The commander drinks juice and eats pasta.
* F8- Only the commander and the pilot are in the command_node.
* F9- The pilot eats beef.
* F10- The crew_mate of the astronaut who drinks water is the specialist.
*/

% Render the solution as a nice table.
:- use_rendering(table,[header(p('Astronaut', 'Role', 'Module', 'Food', 'Drink'))]).

% Two astronauts are crew_mates if they are in the same module.
crew_mates(A1, A2, Ls) :-
    member(p(A1, _, M, _, _), Ls),
    member(p(A2, _, M, _, _), Ls),
    A1 \= A2.

% The facts:
fact1(Ls) :-
    member(p(jo, _, lab_node, _, _), Ls).

fact2(Ls) :-
    % F2 - Alex drinks water.
    member(p(alex, _, _, _, water), Ls).

fact3(Ls) :-
    % F3 - Pat is the pilot.
    member(p(pat, pilot, _, _, _), Ls).

fact4(Ls) :-
    % F4 - The astronaut who eats tofu drinks tea.
    member(p(_, _, _, tofu, tea), Ls).

fact5(Ls) :-
    % F5 - Sam and Pat are crew_mates.
    crew_mates(sam, pat, Ls).

fact6(Ls) :-
    % F6 - Exactly two astronauts are in each module.
    findall(M, member(p(_, _, M, _, _), Ls), Ms),
    include(=(command_node), Ms, CNs),
    include(=(lab_node), Ms, LNs),
    length(CNs, 2),
    length(LNs, 2).

fact7(Ls) :-
    % F7 - The commander drinks juice and eats pasta.
    member(p(_, commander, _, pasta, juice), Ls).

fact8(Ls) :-
    % F8 - Only the commander and the pilot are in the command_node.
    member(p(_, commander, command_node, _, _), Ls),
    member(p(_, pilot,     command_node, _, _), Ls),
    forall(
        member(p(_, Role, command_node, _, _), Ls),
        (Role = commander ; Role = pilot)
    ).

fact9(Ls) :-
    % F9 - The pilot eats beef.
    member(p(_, pilot, _, beef, _), Ls).

fact10(Ls) :-
    % F10 - The crew_mate of the astronaut who drinks water is the specialist.
    member(p(Aw, _, _, _, water), Ls),
    crew_mates(Aw, As, Ls),
    member(p(As, specialist, _, _, _), Ls).

% Problem:
iss_crew(Ls) :-
    length(Ls, 4),                      % There are 4 astronauts

    % TODO add members here
    Ls = [
        p(alex, Ralex, Malex, Falex, Dalex),
        p(sam,  Rsam,  Msam,  Fsam,  Dsam),
        p(jo,   Rjo,   Mjo,   Fjo,   Djo),
        p(pat,  Rpat,  Mpat,  Fpat,  Dpat)
    ],

    % Domains for modules (two modules exist)
    member(Malex, [command_node, lab_node]),
    member(Msam,  [command_node, lab_node]),
    member(Mjo,   [command_node, lab_node]),
    member(Mpat,  [command_node, lab_node]),

    % Unique roles/foods/drinks (exactly one of each)
    permutation([commander, pilot, specialist, engineer],
                [Ralex, Rsam, Rjo, Rpat]),
    permutation([beef, tofu, pasta, curry],
                [Falex, Fsam, Fjo, Fpat]),
    permutation([water, tea, coffee, juice],
                [Dalex, Dsam, Djo, Dpat]),

    fact1(Ls),
    fact2(Ls),
    fact3(Ls),
    fact4(Ls),
    fact5(Ls),
    fact6(Ls),
    fact7(Ls),
    fact8(Ls),
    fact9(Ls),
    fact10(Ls),
    !.

% To see the results, run ?- iss_crew(Ls).
