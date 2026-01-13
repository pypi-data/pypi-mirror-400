"""
Configuration constants for exchanges, currencies, and pairs.
"""

from typing import List, Dict, Set, Optional

# Exchange names (uppercase)
EXCHANGES = ["BINANCE", "NOBITEX", "BITPIN", "KUCOIN", "WALLEX"]

# Base currencies for each exchange
EXCHANGE_BASE_CURRENCIES: Dict[str, List[str]] = {
    "BINANCE": ["USDT"],
    "NOBITEX": ["USDT", "IRT"],
    "BITPIN": ["USDT", "IRT"],
    "KUCOIN": ["USDT"],
    "WALLEX": ["USDT", "IRT"],
}

# Supported currencies for each exchange
EXCHANGE_CURRENCIES: Dict[str, List[str]] = {
    "BINANCE": [
        "1INCH", "ANIME", "BADGER", "BTC", "COW", "DOT", "FIDA", "GNO", "IO", "LINA", "MDT", "NOT", "PENGU", "QKC", "RVN", "STRAX", "TRU", "WAXP", "ZIL",
        "AAVE", "ANKR", "BAKE", "BTTC", "CRV", "DUSK", "FIL", "GNS", "IOST", "LINK", "ME", "NULS", "PEOPLE", "QNT", "S", "STRK", "TRUMP", "WBTC", "ZK",
        "ACA", "ANT", "BAL", "BURGER", "CTK", "DYDX", "FIS", "GRT", "IOTX", "LISTA", "MEME", "OCEAN", "PEPE", "QTUM", "SAGA", "STX", "TRX", "WIF", "ZRO",
        "ACE", "APE", "BANANA", "C98", "CTSI", "DYM", "FLOKI", "GTC", "IQ", "LIT", "METIS", "OGN", "PERP", "RAD", "SAND", "SUI", "TURBO", "WIN", "ZRX",
        "ACH", "API3", "BAND", "CAKE", "CVC", "EDU", "FLOW", "HBAR", "JASMY", "LOOM", "MINA", "OM", "PHA", "RARE", "SCR", "SUPER", "TWT", "WLD",
        "ACT", "APT", "BAT", "CATI", "CVX", "EGLD", "FLUX", "HEI", "JOE", "LPT", "MIR", "OMG", "PHB", "RAY", "SEI", "SUSHI", "UMA", "WOO",
        "ACX", "AR", "BCH", "CELO", "CYBER", "EIGEN", "FORM", "HFT", "JST", "LQTY", "MKR", "OMNI", "PIXEL", "RDNT", "SFP", "SXP", "UNFI", "WTC",
        "ADA", "ARB", "BEL", "CELR", "D", "ELF", "FORTH", "HIFI", "JTO", "LRC", "MLN", "ONDO", "PLUME", "RED", "SHIB", "SYN", "UNI", "XAI",
        "ADX", "ARK", "BETA", "CETUS", "DAR", "ENA", "FRONT", "HIGH", "JUP", "LSK", "MORPHO", "ONE", "PNUT", "REEF", "SKL", "SYRUP", "USDC", "XEM",
        "AERGO", "ARKM", "BICO", "CFX", "DASH", "ENJ", "FTM", "HMSTR", "KAIA", "LTC", "MOVE", "ONG", "POL", "REN", "SLF", "SYS", "UTK", "XLM",
        "AEVO", "ARPA", "BIGTIME", "CGPT", "DATA", "ENS", "FTT", "HNT", "KAITO", "LTO", "MOVR", "ONT", "POLS", "RENDER", "SLP", "T", "VANA", "XMR",
        "AGLD", "ASTR", "BIO", "CHR", "DCR", "EOS", "FXS", "HOOK", "KAVA", "LUMIA", "MTL", "OP", "POLY", "REP", "SNT", "TAO", "VANRY", "XRP",
        "AION", "ATA", "BLUR", "CHZ", "DENT", "EPIC", "G", "HOT", "KDA", "LUNA", "NEAR", "ORCA", "POLYX", "REQ", "SNX", "THE", "VET", "XTZ",
        "AIXBT", "ATOM", "BLZ", "CKB", "DEXE", "ERN", "GALA", "ICP", "KEY", "MAGIC", "NEIRO", "ORDI", "POND", "REZ", "SOL", "THETA", "VGX", "XVG",
        "AKRO", "AUCTION", "BNB", "CLV", "DGB", "ETC", "GAS", "ICX", "KLAY", "MANA", "NEO", "ORN", "PORTAL", "RLC", "SRM", "TIA", "VIC", "XVS",
        "ALGO", "AUDIO", "BNT", "COMBO", "DIA", "ETH", "GHST", "ID", "KMD", "MANTA", "NEXO", "OSMO", "POWR", "RNDR", "SSV", "TLM", "VIRTUAL", "YFI",
        "ALICE", "AVA", "BNX", "COMP", "DNT", "ETHFI", "GLM", "IDEX", "KMNO", "MASK", "NFP", "OXT", "PROM", "ROSE", "STEEM", "TNSR", "VTHO", "YFII",
        "ALPHA", "AVAX", "BOME", "COOKIE", "DODO", "EUR", "GLMR", "ILV", "KNC", "MATIC", "NIL", "PARTI", "PUNDIX", "RPL", "STG", "TOMO", "W", "YGG",
        "ALT", "AXL", "BOND", "COS", "DOGE", "F", "GMT", "IMX", "KSM", "MAV", "NKN", "PAXG", "PYR", "RSR", "STMX", "TON", "WAVES", "ZEC",
        "AMP", "AXS", "BONK", "COTI", "DOGS", "FET", "GMX", "INJ", "LDO", "MBOX", "NMR", "PENDLE", "PYTH", "RUNE", "STORJ", "TRB", "WAVES", "ZEN",
    ],
    "NOBITEX": [
        "100K_FLOKI", "ADA", "APT", "BARD", "CAKE", "DAI", "ENA", "FLUID", "HOT", "KMNO", "MATIC", "NEIRO", "PMN", "RSR", "SSV", "TRX", "WOO", "ZORA",
        "1B_BABYDOGE", "AERO", "ARB", "BAT", "CATI", "DAO", "ENJ", "FORM", "ILV", "LA", "MDT", "NEXO", "PNUT", "S", "STORJ", "TURBO", "X", "ZRO",
        "1INCH", "AEVO", "ASTER", "BCH", "CELR", "DEXE", "ENS", "FTM", "IMX", "LAYER", "ME", "NMR", "POL", "SAFE", "STRK", "UMA", "XAUT", "ZRX",
        "1K_BONK", "AGIX", "AT", "BEAM", "CFX", "DOGE", "EOS", "G", "INCH", "LDO", "MEME", "NOT", "PROM", "SAHARA", "SUI", "UNI", "XLM",
        "1K_CAT", "AGLD", "ATH", "BEAMX", "CGPT", "DOGS", "ETC", "GAL", "INJ", "LINEA", "MET", "OM", "PROVE", "SAND", "SUN", "USDC", "XMR",
        "1K_CHEEMS", "AIXBT", "ATOM", "BICO", "CHZ", "DOOD", "ETH", "GALA", "IO", "LINK", "METIS", "OMG", "PUMP", "SEI", "SUPER", "USDE", "XRP",
        "1K_SHIB", "ALGO", "AVAX", "BIO", "COMP", "DOT", "ETHFI", "GIGGLE", "IOTX", "LPT", "MEW", "ONDO", "PYTH", "SHIB", "SUSHI", "VIRTUAL", "XTZ",
        "1M_BTT", "ALT", "AVNT", "BLUR", "COOKIE", "DYDX", "EUL", "GLM", "JASMY", "LRC", "MKR", "ONE", "QNT", "SKL", "SYRUP", "W", "YFI",
        "1M_NFT", "AMP", "AXL", "BNB", "COTI", "EDU", "FET", "GMT", "JST", "LTC", "MMT", "OP", "RAY", "SKY", "T", "WAL", "ZEC",
        "1M_PEPE", "ANKR", "AXS", "BNX", "CRV", "EGALA", "FIL", "GMX", "JTO", "MAGIC", "MOODENG", "ORCA", "RDNT", "SLP", "TNSR", "WBTC", "ZEN",
        "2Z", "ANT", "BAL", "BOME", "CTC", "EGLD", "FLOKI", "GRT", "JUP", "MAJOR", "MORPHO", "PAXG", "RED", "SNT", "TON", "WET", "ZIL",
        "A", "APE", "BANANA", "BTC", "CVC", "EIGEN", "FLOW", "HBAR", "KAITO", "MANA", "MOVE", "PENDLE", "RENDER", "SNX", "TOSHI", "WIF", "ZKC",
        "AAVE", "API3", "BAND", "BUSD", "CVX", "ELF", "FLR", "HMSTR", "KITE", "MASK", "NEAR", "PENGU", "RNDR", "SOL", "TRB", "WLD", "ZKJ",
    ],
    "BITPIN": [
        "1INCH", "APE", "BAND", "CATI", "CRCLX", "DOGS", "ETC", "GLM", "HYPE", "LTC", "METIS", "NOT", "PIXFI", "SAFE", "SUI", "TRUMP", "USDC", "XRP",
        "A", "API3", "BAT", "CATS", "CRV", "DOT", "ETH", "GMT", "IMX", "LUNA", "MKR", "NVDAX", "PNUT", "SAND", "SUPER", "TRVL", "VET", "XTZ",
        "AAPLX", "ARB", "BCH", "CELR", "CVC", "DYDX", "ETHFI", "GMX", "INJ", "MAGIC", "MNT", "OM", "POL", "SEI", "SUSHI", "TRX", "VIC", "XVS",
        "AAVE", "ARKM", "BLUM", "CGPT", "CVX", "EDU", "FDUSD", "GOOGLX", "JASMY", "MAJOR", "MOODENG", "ONDO", "QNT", "SKL", "SYRUP", "TSLAX", "VIRTUAL", "YFI",
        "ADA", "ASTER", "BLUR", "CHZ", "CYBER", "EGLD", "FET", "GRT", "JOE", "MANA", "MORPHO", "ONE", "QQQX", "SNX", "T", "TURBO", "W", "ZEC",
        "AEVO", "ATH", "BLZ", "COAI", "DAI", "EIGEN", "FIL", "HBAR", "JST", "MASK", "MOVE", "OP", "RAY", "SOL", "THETA", "TWT", "WAVES", "ZIL",
        "AIXBT", "ATOM", "BNB", "COINX", "DASH", "ENA", "FORM", "HIFI", "LDO", "MDT", "MSTRX", "PAWS", "RDNT", "SPYX", "TNSR", "UMA", "WIF", "ZRO",
        "ALGO", "AVAX", "BNT", "COMP", "DEXE", "ENJ", "FTM", "HMSTR", "LINK", "MELANIA", "NEAR", "PAXG", "REEF", "SSV", "TOMI", "UNFI", "WLD", "ZRX",
        "AMZNX", "AXS", "BTC", "COOKIE", "DFDVX", "ENS", "G", "HOODX", "LPT", "MEMEFI", "NEIROCTO", "PENDLE", "RENDER", "STORJ", "TON", "UNI", "XAUT", "XLM",
        "ANKR", "BAKE", "CAKE", "COTI", "DOGE", "EOS", "GALA", "HOT", "LRC", "METAX", "NMR", "PENGU", "S", "STRK", "TRB", "USD1", "XLM",
    ],
    "KUCOIN": [
        "1INCH", "ANT", "BCH", "CELO", "CVC", "DUSK", "FLOW", "HBAR", "JUP", "LSK", "MINA", "OCEAN", "PERP", "RDNT", "SKL", "SYS", "UNFI", "X",
        "AAVE", "APE", "BICO", "CELR", "CVX", "DYDX", "FLR", "HEI", "KAITO", "LTO", "MKR", "OM", "PIXEL", "REN", "SLF", "T", "UNI", "XAI",
        "ACE", "API3", "BIGTIME", "CETUS", "CYBER", "DYM", "FLUX", "HFT", "KAVA", "LUNA", "MLN", "OMG", "PLUME", "RENDER", "SNX", "TAIKO", "UTK", "XAUT",
        "ACH", "APT", "BIO", "CFG", "D", "EDU", "FORM", "HIFI", "KAS", "LUMIA", "MLN", "OMNI", "PNUT", "REP", "SOL", "TAO", "UXLINK", "XDC",
        "ACX", "AR", "BLAST", "CFX", "DAO", "EGLD", "FORTH", "HIGH", "KAVA", "LUNA", "MNT", "ONDO", "POL", "REQ", "SPX", "THETA", "VANA", "XEM",
        "ADA", "ARB", "BLOK", "CGPT", "DAR", "EIGEN", "FTM", "HMSTR", "KDA", "LYX", "MOCA", "ONE", "POLS", "REZ", "SRM", "TIA", "VANRY", "XLM",
        "ADX", "ARKM", "BLUR", "CHILLGUY", "DASH", "ELF", "FTT", "HNT", "KEY", "MAGIC", "MOG", "ONT", "POLYX", "RLC", "SSV", "TLM", "VELO", "XMR",
        "AERGO", "ARPA", "BLZ", "CHR", "DATA", "ELON", "FUEL", "HONEY", "KLAY", "MAJOR", "MOODENG", "OP", "POND", "RLY", "STG", "TNSR", "VET", "XRP",
        "AERO", "ASTR", "BNB", "CHZ", "DBR", "ENA", "FXS", "HYPE", "KMD", "MANA", "MORPHO", "ORCA", "PONKE", "RNDR", "STMX", "TOKEN", "VINU", "XYO",
        "AEVO", "ATA", "BNT", "CKB", "DC", "ENJ", "G", "ICP", "KMNO", "MANTA", "MOVE", "ORDI", "POPCAT", "ROSE", "STORJ", "TOMI", "VIRTUAL", "YFI",
        "AGLD", "ATH", "BOME", "CLV", "DCR", "EOS", "GHST", "ID", "KSM", "MATIC", "MTL", "ORN", "PORTAL", "RPL", "STRAX", "TOMO", "VRA", "YGG",
        "AIXBT", "AUCTION", "BONK", "COMBO", "DEGEN", "EPIC", "GIGA", "ILV", "LDO", "MAV", "MUBI", "OSMO", "POWR", "RSR", "STRK", "TON", "VTHO", "ZEC",
        "AKRO", "AUDIO", "BRETT", "COOKIE", "DENT", "ERN", "GLM", "IMX", "LINA", "MAVIA", "NEAR", "OXT", "PROM", "RUNE", "STX", "TRAC", "W", "ZEN",
        "AKT", "AVA", "BTC", "COTI", "DEXE", "ETC", "GLMR", "INJ", "LINK", "ME", "NEIRO", "PARTI", "PUFFER", "RVN", "SUI", "TRB", "WAL", "ZETA",
        "ALGO", "AVAX", "BTT", "COW", "DGB", "ETH", "GMT", "IO", "LISTA", "MELANIA", "NEO", "PAXG", "PUNDIX", "S", "SUN", "TRU", "WAVES", "ZEUS",
        "ALICE", "AXS", "BURGER", "CPOOL", "DIA", "ETHFI", "GMX", "IOST", "LIT", "MEME", "NFP", "PEAQ", "PYR", "SAFE", "SUSHI", "TRUMP", "WBTC", "ZIL",
        "ALPHA", "BABYDOGE", "C98", "CRO", "DODO", "F", "GNS", "IOTX", "LMWR", "MEMEFI", "NIL", "PENDLE", "PYTH", "SAND", "SWEAT", "TRVL", "WELL", "ZK",
        "ALT", "BAL", "CAKE", "CRV", "DOGE", "FET", "GOAT", "IP", "LOOM", "MERL", "NKN", "PENGU", "QKC", "SCR", "SWELL", "TRX", "WIF", "ZKJ",
        "AMP", "BANANA", "CAT", "CSPR", "DOGS", "FIDA", "GRASS", "JASMY", "LPT", "METIS", "NMR", "PEOPLE", "QNT", "SEI", "SXP", "TURBO", "WIN", "ZRC",
        "ANIME", "BAND", "CATI", "CTC", "DOT", "FIL", "GRT", "JST", "LQTY", "MEW", "NOT", "PEPE", "QTUM", "SFP", "SYN", "TWT", "WLD", "ZRO",
        "ANKR", "BAT", "CATS", "CTSI", "DRIFT", "FLOKI", "GTC", "JTO", "LRC", "MICHI", "NPC", "PEPE2", "RAY", "SHIB", "SYRUP", "UMA", "WOO", "ZRX",
    ],
    "WALLEX": [
        "1BBABYDOGE", "AIXBT", "ATOM", "BNX", "CATS", "DAI", "EIGEN", "FIL", "HMSTR", "KMNO", "MANA", "MORPHO", "ONE", "POLS", "S", "SNX", "TNSR", "VIRTUAL", "XTZ",
        "1INCH", "ALGO", "AVAX", "BOME", "CELR", "DASH", "ELON", "FLOKI", "HOODX", "LAYER", "MASK", "MOVE", "ORCA", "PUMP", "SAFE", "SOL", "TON", "WBTC", "YFI",
        "A", "ALICE", "AXS", "BONK", "CGPT", "DEXE", "ENA", "FLOW", "HOT", "LINEA", "MATIC", "NEAR", "OSMO", "PYTH", "SAHARA", "SPYX", "TRB", "WIF", "ZEC",
        "AAPLX", "AMZNX", "BAL", "BTC", "CHZ", "DOGS", "EOS", "FTM", "IO", "LPT", "MDT", "NEIRO", "PAXG", "RAY", "SEI", "SUI", "TSLAX", "X", "ZIL",
        "AAVE", "APE", "BAND", "BTTC", "COINX", "DOT", "ETC", "GALA", "JASMY", "LRC", "MEME", "NMR", "PENGU", "RBTC", "SHIB", "SUPER", "TURBO", "XAUT", "ZRX",
        "ADA", "APT", "BCH", "BURGER", "COOKIE", "DYDX", "ETH", "GMT", "IMX", "LUNA", "MEMEFI", "NOT", "PEOPLE", "RBTC1", "SAND", "SUSHI", "TRX", "XLM",
        "AEVO", "ARB", "BICO", "CAKE", "CRV", "EDU", "ETHFI", "GRT", "JUP", "LTC", "METAX", "NVDAX", "PEPE", "RDNT", "SKL", "SYRUP", "UMA", "XMR",
        "AGLD", "ASTER", "BIO", "CAT", "CVC", "EGLD", "FET", "HBAR", "KAITO", "MAGIC", "MKR", "OM", "PIXFI", "RENDER", "SKY", "T", "USDC", "XRP",
        "AIOZ", "ATH", "BNB", "CATI", "CVX", "EGALA", "FIL", "HYPE", "LINK", "MAJOR", "MOG", "ONDO", "POL", "RUNE", "SLP", "TNSR", "UMA", "XLM",
    ],
}

# Helper function to get all valid pairs for an exchange
def get_exchange_pairs(exchange: str) -> List[str]:
    """
    Get all valid trading pairs for an exchange.
    
    Args:
        exchange: Exchange name (uppercase)
        
    Returns:
        List of trading pairs in format {CURRENCY}-{BASE_CURRENCY}
    """
    exchange = exchange.upper()
    if exchange not in EXCHANGE_CURRENCIES:
        return []
    
    currencies = EXCHANGE_CURRENCIES[exchange]
    base_currencies = EXCHANGE_BASE_CURRENCIES.get(exchange, [])
    
    pairs = []
    for currency in currencies:
        for base in base_currencies:
            pairs.append(f"{currency}-{base}")
    
    return pairs

# Helper function to validate a pair
def is_valid_pair(pair: str, exchange: Optional[str] = None) -> bool:
    """
    Check if a pair is valid.
    
    Args:
        pair: Trading pair in format {CURRENCY}-{BASE_CURRENCY}
        exchange: Optional exchange name to validate against specific exchange
        
    Returns:
        True if pair is valid
    """
    if "-" not in pair:
        return False
    
    parts = pair.split("-", 1)
    if len(parts) != 2:
        return False
    
    currency, base = parts
    
    if exchange:
        exchange = exchange.upper()
        if exchange not in EXCHANGE_CURRENCIES:
            return False
        if currency not in EXCHANGE_CURRENCIES[exchange]:
            return False
        if base not in EXCHANGE_BASE_CURRENCIES.get(exchange, []):
            return False
    else:
        # Check if currency exists in any exchange
        currency_exists = any(
            currency in currencies 
            for currencies in EXCHANGE_CURRENCIES.values()
        )
        base_exists = any(
            base in bases 
            for bases in EXCHANGE_BASE_CURRENCIES.values()
        )
        if not currency_exists or not base_exists:
            return False
    
    return True

# Helper function to get all pairs across all exchanges
def get_all_pairs() -> List[str]:
    """
    Get all valid trading pairs across all exchanges.
    
    Returns:
        List of all trading pairs
    """
    all_pairs = []
    for exchange in EXCHANGES:
        all_pairs.extend(get_exchange_pairs(exchange))
    return sorted(set(all_pairs))  # Remove duplicates and sort

