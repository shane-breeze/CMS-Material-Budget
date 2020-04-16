import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

def parse_args():
    options = VarParsing("analysis")
    options.register(
        'vtxsmear', 'NoSmear',
        VarParsing.multiplicity.singleton,
        VarParsing.varType.string,
        "Vertex smearing options ('Flat' or 'NoSmear')",
    )
    options.register(
        'genseed', 456789,
        VarParsing.multiplicity.singleton,
        VarParsing.varType.int,
        "Generator initial seed",
    )
    options.register(
        'vtxseed', 98765432,
        VarParsing.multiplicity.singleton,
        VarParsing.varType.int,
        "Vertex smear initial seed",
    )
    options.maxEvents = 10000
    options.outputFile = "single_neutrino.root"
    options.parseArguments()
    return options

def Process():
    process = cms.Process("TestProcess")
    options = parse_args()

    process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
    #process.load("IOMC.EventVertexGenerators.VtxSmearedFlat_cfi")
    from Configuration.StandardSequences.VtxSmeared import VtxSmeared
    process.load(VtxSmeared[options.vtxsmear])
    process.load("GeneratorInterface.Core.generatorSmeared_cfi")
    process.load("Configuration.EventContent.EventContent_cff")
    process.load("IOMC.RandomEngine.IOMC_cff")

    process.maxEvents = cms.untracked.PSet(
        input = cms.untracked.int32(options.maxEvents)
    )

    process.RandomNumberGeneratorService.generator.initialSeed = (
        options.genseed
    )
    process.RandomNumberGeneratorService.VtxSmeared.engineName = (
        cms.untracked.string('HepJamesRandom')
    )
    process.RandomNumberGeneratorService.VtxSmeared.initialSeed = (
        cms.untracked.uint32(options.vtxseed)
    )

    process.source = cms.Source("EmptySource",
        firstRun   = cms.untracked.uint32(1),
        firstEvent = cms.untracked.uint32(1)
    )

    process.generator = cms.EDProducer("FlatRandomEGunProducer",
        PGunParameters = cms.PSet(
            PartID = cms.vint32(14),
            MinEta = cms.double(-5.5),
            MaxEta = cms.double(5.5),
            MinPhi = cms.double(-3.14159265359),
            MaxPhi = cms.double(3.14159265359),
            MinE   = cms.double(10.0),
            MaxE   = cms.double(10.0)
        ),
        AddAntiParticle = cms.bool(False),
        Verbosity       = cms.untracked.int32(0)
    )

    process.o1 = cms.OutputModule("PoolOutputModule",
        process.FEVTSIMEventContent,
        fileName = cms.untracked.string(options.outputFile),
    )

    process.p1 = cms.Path(process.generator*process.VtxSmeared*process.generatorSmeared)
    process.outpath = cms.EndPath(process.o1)
    return process

if __name__ == "__main__":
    process = Process()
