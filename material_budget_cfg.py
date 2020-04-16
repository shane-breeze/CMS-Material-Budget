import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

def parse_args():
    options = VarParsing("analysis")
    options.register(
        'start', 0,
        VarParsing.multiplicity.singleton,
        VarParsing.varType.int,
        "First event",
    )
    options.register(
        'stop', 100,
        VarParsing.multiplicity.singleton,
        VarParsing.varType.int,
        "Last event + 1",
    )
    options.register(
        'genseed', 456789,
        VarParsing.multiplicity.singleton,
        VarParsing.varType.int,
        "Generator initial seed",
    )
    options.register(
        'simseed', 9876,
        VarParsing.multiplicity.singleton,
        VarParsing.varType.int,
        "Geant4 simulated hits' initial seed",
    )
    options.parseArguments()
    return options

def Process():
    process = cms.Process("PROD")
    options = parse_args()

    process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
    process.load("Configuration.Geometry.GeometryExtended2017Plan1_cff")
    process.load("Geometry.TrackerNumberingBuilder.trackerNumberingGeometry_cfi")
    process.load("Configuration.StandardSequences.MagneticField_38T_cff")
    process.load("SimG4Core.Application.g4SimHits_cfi")
    process.load("IOMC.RandomEngine.IOMC_cff")
    process.RandomNumberGeneratorService.generator.initialSeed = options.genseed
    process.RandomNumberGeneratorService.g4SimHits.initialSeed = options.simseed

    process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(options.inputFiles),
        eventsToProcess = cms.untracked.VEventRange(
            '1:{}-1:{}'.format(options.start, options.stop-1),
        ),
    )

    process.maxEvents = cms.untracked.PSet(
        input = cms.untracked.int32(options.maxEvents)
    )

    dets = [
        {"label": "Beam", "volumes": ["BEAM", "BEAM1", "BEAM2", "BEAM3"]},
        {"label": "Tracker", "volumes": ["Tracker"]},
        {"label": "ECAL", "volumes": ["ECAL"]},
        {"label": "HCAL", "volumes": ["HCal", "VCAL"]},
        {"label": "Magnet", "volumes": ["MGNT"]},
        {"label": "Muon", "volumes": ["MB", "MEP", "MEN"]},
    ]

    process.p1 = cms.Path(process.g4SimHits)
    process.g4SimHits.StackingAction.TrackNeutrino = cms.bool(True)
    process.g4SimHits.UseMagneticField = False
    process.g4SimHits.Physics.type = 'SimG4Core/Physics/DummyPhysics'
    process.g4SimHits.Physics.DummyEMPhysics = True
    process.g4SimHits.Physics.CutsPerRegion = False
    process.g4SimHits.Watchers = cms.VPSet(
        *[cms.PSet(
            type = cms.string('MaterialBudgetAction'),
            MaterialBudgetAction = cms.PSet(
                HistosFile       = cms.string("None"),
                AllStepsToTree   = cms.bool(False),
                HistogramList    = cms.string('None'),
                SelectedVolumes  = cms.vstring(det["volumes"]),
                TreeFile         = cms.string(options.outputFile.format(det["label"])),
                StopAfterProcess = cms.string("None"),
                TextFile         = cms.string("None"),
            ),
        ) for det in dets]
    )
    return process

if __name__ == "__main__":
    process = Process()

