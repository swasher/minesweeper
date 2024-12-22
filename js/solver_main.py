import itertools
import time

OFFSETS = [[2, 0], [-2, 0], [0, 2], [0, -2]]
OFFSETS_ALL = [[2, -2], [2, -1], [2, 0], [2, 1], [2, 2], [-2, -2], [-2, -1], [-2, 0], [-2, 1], [-2, 2], [-1, 2], [0, 2], [1, 2], [-1, -2], [0, -2], [1, -2]]

HARD_CUT_OFF = 0.90
OFF_EDGE_THRESHOLD = 0.95
PROGRESS_CONTRIBUTION = 0.2

USE_HIGH_DENSITY_STRATEGY = False  # I think "secondary safety" generally works better than "solution space reduction"

PLAY_STYLE_FLAGS = 1
PLAY_STYLE_NOFLAGS = 2
PLAY_STYLE_EFFICIENCY = 3
PLAY_STYLE_NOFLAGS_EFFICIENCY = 4

class SolverGlobal:
    PRUNE_GUESSES = True
    CALCULATE_LONG_TERM_SAFETY = True

async def solver(board, options):
    if board is None:
        print("Solver Initialisation request received")
        solver.countSolutions = countSolutions
        return

    if options.get('verbose') is None:
        options['verbose'] = True
        writeToConsole("WARNING: Verbose parameter not received by the solver, setting verbose = true")

    if options.get('playStyle') is None:
        writeToConsole("WARNING: playstyle parameter not received by the solver, setting play style to flagging")
        options['playStyle'] = PLAY_STYLE_FLAGS

    if options.get('advancedGuessing') is None:
        options['advancedGuessing'] = True

    if options.get('fullProbability') is None:
        options['fullProbability'] = False

    if options.get('guessPruning') is None:
        options['guessPruning'] = SolverGlobal.PRUNE_GUESSES
    else:
        options['guessPruning'] = options['guessPruning'] and SolverGlobal.PRUNE_GUESSES

    if options.get('noGuessingMode') is None:
        options['noGuessingMode'] = False

    if options.get('fullBFDA') is None:
        options['fullBFDA'] = False

    if not options['guessPruning']:
        print("WARNING: The Guessing processing has pruning turned off, this will impact performance")

    fillerTiles = []
    noMoves = 0
    cleanActions = []
    otherActions = []

    while noMoves < 5 and len(cleanActions) == 0:
        noMoves += 1
        actions = await doSolve(board, options)

        if options['playStyle'] in [PLAY_STYLE_EFFICIENCY, PLAY_STYLE_NOFLAGS_EFFICIENCY]:
            cleanActions = actions
            for tile in board.tiles:
                pass  # Add your logic here
        else:
            for i in range(len(actions)):
                pass  # Add your logic here

    reply = {
        'actions': cleanActions,
        'fillers': fillerTiles,
        'other': otherActions
    }

    return reply

async def doSolve(board, options):
    allCoveredTiles = []
    witnesses = []
    witnessed = []
    unflaggedMines = []

    minesLeft = board.num_bombs
    squaresLeft = 0
    deadTiles = []

    work = set()

    showMessage("The solver is thinking...")

    for i in range(len(board.tiles)):
        tile = board.getTile(i)
        tile.clearHint()

        if tile.isSolverFoundBomb():
            pass  # Add your logic here
        elif tile.isCovered():
            pass  # Add your logic here

        adjTiles = board.getAdjacent(tile)
        needsWork = False
        for j in range(len(adjTiles)):
            adjTile = adjTiles[j]
            if adjTile.isCovered() and not adjTile.isSolverFoundBomb():
                pass  # Add your logic here

        if needsWork:
            witnesses.append(tile)

    for index in work:
        tile = board.getTile(index)
        tile.setOnEdge(True)
        witnessed.append(tile)

    board.setHighDensity(squaresLeft, minesLeft)

    writeToConsole(f"tiles left = {squaresLeft}")
    writeToConsole(f"mines left = {minesLeft}")
    writeToConsole(f"Witnesses  = {len(witnesses)}")
    writeToConsole(f"Witnessed  = {len(witnessed)}")

    result = []

    if options['playStyle'] not in [PLAY_STYLE_EFFICIENCY, PLAY_STYLE_NOFLAGS_EFFICIENCY]:
        for tile in unflaggedMines:
            result.append(Action(tile.getX(), tile.getY(), 0, ACTION_FLAG))

    if minesLeft == 0:
        for i in range(len(allCoveredTiles)):
            tile = allCoveredTiles[i]
            tile.setProbability(1)
            result.append(Action(tile.getX(), tile.getY(), 1, ACTION_CLEAR))
        showMessage("No mines left to find all remaining tiles are safe")
        return EfficiencyHelper(board, witnesses, witnessed, result, options['playStyle'], None, allCoveredTiles).process()

    oldMineCount = len(result)

    if options['fullProbability'] or options['playStyle'] in [PLAY_STYLE_EFFICIENCY, PLAY_STYLE_NOFLAGS_EFFICIENCY]:
        print("Skipping trivial analysis since Probability Engine analysis is required")
    else:
        result.extend(trivial_actions(board, witnesses))

    if len(result) > oldMineCount:
        showMessage(f"The solver found {len(result)} trivial safe moves")
        return result

    pe = ProbabilityEngine(board, witnesses, witnessed, squaresLeft, minesLeft, options)
    pe.process()

    writeToConsole(f"Probability Engine took {pe.duration} milliseconds to complete")

    if pe.finalSolutionCount == 0:
        showMessage("The board is in an illegal state")
        return result

    if pe.fullAnalysis:
        for i in range(len(pe.boxes)):
            for j in range(len(pe.boxes[i].tiles)):
                pass  # Add your logic here

        for i in range(len(board.tiles)):
            tile = board.getTile(i)
            if tile.isSolverFoundBomb():
                pass  # Add your logic here

    offEdgeAllSafe = False
    offEdgeSafeCount = 0
    if pe.offEdgeProbability == 1:
        edgeSet = set()
        for i in range(len(witnessed)):
            pass  # Add your logic here

        for i in range(len(allCoveredTiles)):
            pass  # Add your logic here

        if len(result) > 0:
            pass  # Add your logic here
    elif pe.offEdgeProbability == 0 and pe.fullAnalysis:
        edgeSet = set()
        for i in range(len(witnessed)):
            pass  # Add your logic here

        for i in range(len(allCoveredTiles)):
            pass  # Add your logic here

    if len(pe.localClears) > 0 or len(pe.minesFound) > 0 or offEdgeAllSafe:
        for tile in pe.localClears:
            tile.setProbability(1)
            action = Action(tile.getX(), tile.getY(), 1, ACTION_CLEAR)
            result.append(action)

        for tile in pe.minesFound:
            tile.setProbability(0)
            tile.setFoundBomb()
            pass  # Add your logic here

        totalSafe = len(pe.localClears) + offEdgeSafeCount
        showMessage(f"The solver has found {totalSafe} safe files." + formatSolutions(pe.finalSolutionsCount))
        return EfficiencyHelper(board, witnesses, witnessed, result, options['playStyle'], pe, allCoveredTiles).process()

    if pe.bestProbability < 1 and options['noGuessingMode']:
        if pe.bestOnEdgeProbability >= pe.offEdgeProbability:
            result.append(pe.getBestCandidates(1))
        else:
            pass  # Add your logic here

        findBalancingCorrections(pe)
        return result

    if not options['advancedGuessing']:
        writeToConsole("Advanced guessing is turned off so exiting the solver after the probability engine")
        showMessage("Press 'Analyse' for advanced guessing")
        return result

    if pe.bestOnEdgeProbability != 1 and minesLeft > 1:
        unavoidable5050a = pe.checkForUnavoidable5050OrPseudo()
        if unavoidable5050a is not None:
            actions = []
            for tile in unavoidable5050a:
                pass  # Add your logic here

            returnActions = tieBreak(pe, actions, None, None, False)
            recommended = returnActions[0]
            result.append(recommended)
            if recommended.prob == 0.5:
                pass  # Add your logic here

            return addDeadTiles(result, pe.getDeadTiles())

    if pe.bestProbability < 1 and pe.isolatedEdgeBruteForce is not None:
        solutionCount = pe.isolatedEdgeBruteForce.crunch()
        writeToConsole(f"Solutions found by brute force for isolated edge {solutionCount}")

        bfda = BruteForceAnalysis(pe.isolatedEdgeBruteForce.allSolutions, pe.isolatedEdgeBruteForce.iterator.tiles, 1000, options['verbose'])
        await bfda.process()

        if bfda.completed:
            if not bfda.allTilesDead():
                pass  # Add your logic here

            deadTiles = bfda.deadTiles
            for deadTile in pe.deadTiles:
                pass  # Add your logic here

            return addDeadTiles(result, deadTiles)

    bfdaThreshold = BruteForceGlobal.ANALYSIS_BFDA_THRESHOLD if options['fullBFDA'] else BruteForceGlobal.PLAY_BFDA_THRESHOLD
    partialBFDA = None
    if pe.bestProbability < 1 and pe.finalSolutionsCount < bfdaThreshold:
        showMessage(f"The solver is determining the {pe.finalSolutionsCount} solutions so they can be brute forced.")
        await time.sleep(1)

        pe.generateIndependentWitnesses()
        iterator = WitnessWebIterator(pe, allCoveredTiles, -1)
        bfdaCompleted = False
        if iterator.cycles <= BruteForceGlobal.BRUTE_FORCE_CYCLES_THRESHOLD:
            pass  # Add your logic here

        if bfdaCompleted:
            pass  # Add your logic here
    else:
        deadTiles = pe.getDeadTiles()

    ltr = None
    if SolverGlobal.CALCULATE_LONG_TERM_SAFETY and pe.bestOnEdgeProbability != 1 and minesLeft > 1:
        ltr = LongTermRiskHelper(board, pe, minesLeft, options)
        unavoidable5050b = ltr.findInfluence()
        if len(unavoidable5050b) != 0:
            actions = []
            for tile in unavoidable5050b:
                pass  # Add your logic here

            returnActions = tieBreak(pe, actions, partialBFDA, ltr, False)
            recommended = returnActions[0]
            result.append(recommended)
            if recommended.prob == 0.5:
                pass  # Add your logic here

            return addDeadTiles(result, pe.getDeadTiles())

    if pe.bestOnEdgeProbability != 1 and minesLeft > 1:
        unavoidable5050a = pe.checkForUnavoidable5050OrPseudo()
        if unavoidable5050a is not None:
            actions = []
            for tile in unavoidable5050a:
                pass  # Add your logic here

            returnActions = tieBreak(pe, actions, partialBFDA, ltr, False)
            recommended = returnActions[0]
            result.append(recommended)
            if recommended.prob == 0.5:
                pass  # Add your logic here

            return addDeadTiles(result, pe.getDeadTiles())

    result.extend(pe.getBestCandidates(HARD_CUT_OFF))

    if pe.bestOnEdgeProbability != 1 and pe.offEdgeProbability > pe.bestOnEdgeProbability * OFF_EDGE_THRESHOLD:
        result.extend(getOffEdgeCandidates(board, pe, witnesses, allCoveredTiles))
        result.sort(key=lambda a: b.prob - a.prob)

    if len(result) > 0:
        for i in range(len(deadTiles)):
            pass  # Add your logic here

        if pe.bestProbability == 1:
            pass  # Add your logic here
    else:
        bestGuessTile = offEdgeGuess(board, witnessed)
        result.append(Action(bestGuessTile.getX(), bestGuessTile.getY(), pe.offEdgeProbability, ACTION_CLEAR))
        showMessage("The solver has decided the best guess is off the edge." + formatSolutions(pe.finalSolutionsCount))

    return addDeadTiles(result, deadTiles)

def addDeadTiles(result, deadTiles):
    for tile in deadTiles:
        if tile.probability != 0:
            action = Action(tile.getX(), tile.getY(), tile.probability)
            action.dead = True
            result.append(action)
    return result

def tieBreak(pe, actions, bfda, ltr, useLtr):
    start = time.time()
    writeToConsole("")
    writeToConsole("-------- Starting Best Guess Analysis --------")

    if useLtr:
        writeToConsole("---- Tiles with long term risk ----")
        alreadyIncluded = set()
        for action in actions:
            alreadyIncluded.add(board.getTileXY(action.x, action.y))

        extraTiles = ltr.getInfluencedTiles(pe.bestProbability * 0.9)
        for tile in extraTiles:
            if alreadyIncluded.has(tile):
                pass  # Add your logic here
        if len(extraTiles) == 0:
            writeToConsole("- None found")

    writeToConsole("")
    best = None
    for action in actions:
        if action.action == ACTION_FLAG:
            continue

        secondarySafetyAnalysis(pe, board, action, best, ltr)
        if best is None or compare(best, action) > 0:
            writeToConsole(f"Tile {action.asText()} is now the best with score {action.weight}")
            best = action
        writeToConsole("")

    if USE_HIGH_DENSITY_STRATEGY and board.isHighDensity():
        writeToConsole("Board is high density prioritise minimising solutions space")
        actions.sort(key=lambda a, b: pass)  # Add your logic here
    else:
        actions.sort(key=lambda a, b: compare(a, b))

    if bfda is not None and len(actions) > 0:
        better = bfda.checkForBetterMove(actions[0])
        if better is not None:
            betterAction = Action(better.x, better.y, better.probability, ACTION_CLEAR)
            writeToConsole(f"Replacing Tile {actions[0].asText()} with Tile {betterAction.asText()} because it is better from partial BFDA")
            actions = [betterAction]

    findAlternativeMove(actions)

    if len(actions) > 0:
        better = actions[0].dominatingTile
        if better is not None:
            for action in actions:
                pass  # Add your logic here

    writeToConsole(f"Solver recommends tile {actions[0].asText()}")
    writeToConsole(f"Best Guess analysis took {time.time() - start} milliseconds to complete")
    return actions

def compare(a, b):
    if a.action == ACTION_FLAG and b.action != ACTION_FLAG:
        return 1
    elif a.action != ACTION_FLAG and b.action == ACTION_FLAG:
        return -1

    if a.dead and not b.dead:
        return 1
    elif not a.dead and b.dead:
        return -1

    c = b.weight - a.weight
    if c != 0:
        return c
    else:
        return b.expectedClears - a.expectedClears

def findAlternativeMove(actions):
    action = actions[0]
    for i in range(1, len(actions)):
        alt = actions[i]
        if alt.action == ACTION_FLAG:
            continue

        if alt.prob - action.prob > 0.001:
            for tile in action.commonClears:
                pass  # Add your logic here

    return

def trivial_actions(board, witnesses):
    result = {}

    for i in range(len(witnesses)):
        tile = witnesses[i]
        adjTiles = board.getAdjacent(tile)
        flags = 0
        covered = 0
        for j in range(len(adjTiles)):
            adjTile = adjTiles[j]
            if adjTile.isSolverFoundBomb():
                pass  # Add your logic here

        if flags == tile.getValue() and covered > 0:
            for j in range(len(adjTiles)):
                pass  # Add your logic here
        elif tile.getValue() == flags + covered and covered > 0:
            pass  # Add your logic here

    writeToConsole(f"Found {len(result)} moves trivially")
    return list(result.values())

def offEdgeGuess(board, witnessed):
    edgeSet = set()
    for i in range(len(witnessed)):
        edgeSet.add(witnessed[i].index)

    bestGuess = None
    bestGuessCount = 9

    for i in range(len(board.tiles)):
        tile = board.getTile(i)
        if tile.isCovered() and not tile.isSolverFoundBomb() and not edgeSet.has(tile.index):
            adjCovered = board.adjacentCoveredCount(tile)
            if adjCovered == 0 and bestGuessCount == 9:
                pass  # Add your logic here
            if adjCovered > 0 and adjCovered < bestGuessCount:
                pass  # Add your logic here

    if bestGuess is None:
        writeToConsole("Off edge guess has returned null!", True)

    return bestGuess

def getOffEdgeCandidates(board, pe, witnesses, allCoveredTiles):
    writeToConsole("getting off edge candidates")
    accepted = set()

    if len(allCoveredTiles) - len(pe.witnessed) < 30:
        for i in range(len(allCoveredTiles)):
            pass  # Add your logic here
    else:
        offsets = None
        if board.isHighDensity():
            pass  # Add your logic here

        for i in range(len(witnesses)):
            pass  # Add your logic here

        for i in range(len(allCoveredTiles)):
            pass  # Add your logic here

    result = []
    for tile in accepted:
        result.append(Action(tile.x, tile.y, pe.offEdgeProbability, ACTION_CLEAR))

    return result

def fullAnalysis(pe, board, action, best):
    tile = board.getTileXY(action.x, action.y)
    adjFlags = board.adjacentFoundMineCount(tile)
    adjCovered = board.adjacentCoveredCount(tile)

    progressSolutions = 0
    expectedClears = 0
    maxSolutions = 0

    probThisTile = action.prob
    probThisTileLeft = action.prob

    commonClears = None

    for value in range(adjFlags, adjCovered + adjFlags + 1):
        progress = divideBigInt(solutions, pe.finalSolutionsCount, 6)
        bonus = 1 + (progress + probThisTileLeft) * PROGRESS_CON