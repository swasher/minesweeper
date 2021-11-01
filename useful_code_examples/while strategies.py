while do_random:
    # input('lets R1...')
    do_strategy(solver_R1)

    have_a_move_B2 = True
    # input('lets B2...')
    while have_a_move_B2:
        have_a_move_B2 = do_strategy(solver_B2)

        have_a_move_E2 = True
        # input('lets E2...')
        while have_a_move_E2:
            have_a_move_E2 = do_strategy(solver_E2)

            have_a_move_B1 = True
            while have_a_move_B1:
                have_a_move_B1 = do_strategy(solver_B1)

                have_a_move_E1 = True
                while have_a_move_E1:
                    have_a_move_E1 = do_strategy(solver_E1)


strat = [solver_E2, solver_B2, solver_E1, solver_B1, solver_R1]