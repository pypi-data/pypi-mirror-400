#!/usr/bin/env python3
"""
Stdio MCP Server for Medical APIs
Provides stdio interface for the unified medical MCP server
"""

import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)

# Initialize Sentry first - must happen before server imports
from medical_mcps.sentry_config import init_sentry
from medical_mcps.settings import settings

init_sentry()

log = logging.getLogger(__name__)

# Import unified_mcp after server imports so tools are registered
from medical_mcps.med_mcp_server import unified_mcp
from medical_mcps.servers import (
    biothings_server,
    chembl_server,
    ctg_server,
    gwas_server,
    kegg_server,
    myvariant_server,
    nci_server,
    nodenorm_server,
    omim_server,
    openfda_server,
    opentargets_server,
    pathwaycommons_server,
    pubmed_server,
    reactome_server,
    uniprot_server,
)
from medical_mcps.servers import (
    neo4j_server as everycure_kg_server,
)

async def main():
    """Main stdio server entry point"""
    log.info("Starting Medical APIs MCP Server (stdio)...")
    log.info("Available tools from unified server")
    
    # Use FastMCP's stdio server
    await unified_mcp.run_stdio()

def entry_point():
    """Entry point for the script command"""
    asyncio.run(main())

if __name__ == "__main__":
    entry_point()
