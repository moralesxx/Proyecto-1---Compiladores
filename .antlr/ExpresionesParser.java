// Generated from /home/morxx/Compiladores/Expresiones.g by ANTLR 4.13.1
import org.antlr.v4.runtime.atn.*;
import org.antlr.v4.runtime.dfa.DFA;
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.misc.*;
import org.antlr.v4.runtime.tree.*;
import java.util.List;
import java.util.Iterator;
import java.util.ArrayList;

@SuppressWarnings({"all", "warnings", "unchecked", "unused", "cast", "CheckReturnValue"})
public class ExpresionesParser extends Parser {
	static { RuntimeMetaData.checkVersion("4.13.1", RuntimeMetaData.VERSION); }

	protected static final DFA[] _decisionToDFA;
	protected static final PredictionContextCache _sharedContextCache =
		new PredictionContextCache();
	public static final int
		PROGRAMA=1, SI=2, SINO=3, TIPO=4, LLAVE_IZQ=5, LLAVE_DER=6, PAR_IZQ=7, 
		PAR_DER=8, PUNTO_COMA=9, ASIGNACION=10, SUMA=11, RESTA=12, MULT=13, DIV=14, 
		MAYOR=15, MENOR=16, IGUAL=17, DIFERENTE=18, MAYOR_IGUAL=19, MENOR_IGUAL=20, 
		Y_LOGICO=21, O_LOGICO=22, NO_LOGICO=23, ID=24, NUMERO=25, WS=26, COMENTARIO=27;
	public static final int
		RULE_root = 0, RULE_instrucciones = 1, RULE_bloque = 2, RULE_declaracion = 3, 
		RULE_asignacion = 4, RULE_condicion = 5, RULE_expr = 6;
	private static String[] makeRuleNames() {
		return new String[] {
			"root", "instrucciones", "bloque", "declaracion", "asignacion", "condicion", 
			"expr"
		};
	}
	public static final String[] ruleNames = makeRuleNames();

	private static String[] makeLiteralNames() {
		return new String[] {
			null, "'program'", "'if'", "'else'", null, "'{'", "'}'", "'('", "')'", 
			"';'", "'='", "'+'", "'-'", "'*'", "'/'", "'>'", "'<'", "'=='", null, 
			"'>='", "'<='", "'&&'", "'||'", "'!'"
		};
	}
	private static final String[] _LITERAL_NAMES = makeLiteralNames();
	private static String[] makeSymbolicNames() {
		return new String[] {
			null, "PROGRAMA", "SI", "SINO", "TIPO", "LLAVE_IZQ", "LLAVE_DER", "PAR_IZQ", 
			"PAR_DER", "PUNTO_COMA", "ASIGNACION", "SUMA", "RESTA", "MULT", "DIV", 
			"MAYOR", "MENOR", "IGUAL", "DIFERENTE", "MAYOR_IGUAL", "MENOR_IGUAL", 
			"Y_LOGICO", "O_LOGICO", "NO_LOGICO", "ID", "NUMERO", "WS", "COMENTARIO"
		};
	}
	private static final String[] _SYMBOLIC_NAMES = makeSymbolicNames();
	public static final Vocabulary VOCABULARY = new VocabularyImpl(_LITERAL_NAMES, _SYMBOLIC_NAMES);

	/**
	 * @deprecated Use {@link #VOCABULARY} instead.
	 */
	@Deprecated
	public static final String[] tokenNames;
	static {
		tokenNames = new String[_SYMBOLIC_NAMES.length];
		for (int i = 0; i < tokenNames.length; i++) {
			tokenNames[i] = VOCABULARY.getLiteralName(i);
			if (tokenNames[i] == null) {
				tokenNames[i] = VOCABULARY.getSymbolicName(i);
			}

			if (tokenNames[i] == null) {
				tokenNames[i] = "<INVALID>";
			}
		}
	}

	@Override
	@Deprecated
	public String[] getTokenNames() {
		return tokenNames;
	}

	@Override

	public Vocabulary getVocabulary() {
		return VOCABULARY;
	}

	@Override
	public String getGrammarFileName() { return "Expresiones.g"; }

	@Override
	public String[] getRuleNames() { return ruleNames; }

	@Override
	public String getSerializedATN() { return _serializedATN; }

	@Override
	public ATN getATN() { return _ATN; }

	public ExpresionesParser(TokenStream input) {
		super(input);
		_interp = new ParserATNSimulator(this,_ATN,_decisionToDFA,_sharedContextCache);
	}

	@SuppressWarnings("CheckReturnValue")
	public static class RootContext extends ParserRuleContext {
		public RootContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_root; }
	 
		public RootContext() { }
		public void copyFrom(RootContext ctx) {
			super.copyFrom(ctx);
		}
	}
	@SuppressWarnings("CheckReturnValue")
	public static class ProgContext extends RootContext {
		public TerminalNode PROGRAMA() { return getToken(ExpresionesParser.PROGRAMA, 0); }
		public TerminalNode LLAVE_IZQ() { return getToken(ExpresionesParser.LLAVE_IZQ, 0); }
		public TerminalNode LLAVE_DER() { return getToken(ExpresionesParser.LLAVE_DER, 0); }
		public TerminalNode EOF() { return getToken(ExpresionesParser.EOF, 0); }
		public List<InstruccionesContext> instrucciones() {
			return getRuleContexts(InstruccionesContext.class);
		}
		public InstruccionesContext instrucciones(int i) {
			return getRuleContext(InstruccionesContext.class,i);
		}
		public ProgContext(RootContext ctx) { copyFrom(ctx); }
	}

	public final RootContext root() throws RecognitionException {
		RootContext _localctx = new RootContext(_ctx, getState());
		enterRule(_localctx, 0, RULE_root);
		int _la;
		try {
			_localctx = new ProgContext(_localctx);
			enterOuterAlt(_localctx, 1);
			{
			setState(14);
			match(PROGRAMA);
			setState(15);
			match(LLAVE_IZQ);
			setState(17); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(16);
				instrucciones();
				}
				}
				setState(19); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( (((_la) & ~0x3f) == 0 && ((1L << _la) & 16777236L) != 0) );
			setState(21);
			match(LLAVE_DER);
			setState(22);
			match(EOF);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class InstruccionesContext extends ParserRuleContext {
		public InstruccionesContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_instrucciones; }
	 
		public InstruccionesContext() { }
		public void copyFrom(InstruccionesContext ctx) {
			super.copyFrom(ctx);
		}
	}
	@SuppressWarnings("CheckReturnValue")
	public static class InstrAsigContext extends InstruccionesContext {
		public AsignacionContext asignacion() {
			return getRuleContext(AsignacionContext.class,0);
		}
		public TerminalNode PUNTO_COMA() { return getToken(ExpresionesParser.PUNTO_COMA, 0); }
		public InstrAsigContext(InstruccionesContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class InstrDeclContext extends InstruccionesContext {
		public DeclaracionContext declaracion() {
			return getRuleContext(DeclaracionContext.class,0);
		}
		public TerminalNode PUNTO_COMA() { return getToken(ExpresionesParser.PUNTO_COMA, 0); }
		public InstrDeclContext(InstruccionesContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class InstrIfContext extends InstruccionesContext {
		public TerminalNode SI() { return getToken(ExpresionesParser.SI, 0); }
		public TerminalNode PAR_IZQ() { return getToken(ExpresionesParser.PAR_IZQ, 0); }
		public CondicionContext condicion() {
			return getRuleContext(CondicionContext.class,0);
		}
		public TerminalNode PAR_DER() { return getToken(ExpresionesParser.PAR_DER, 0); }
		public List<BloqueContext> bloque() {
			return getRuleContexts(BloqueContext.class);
		}
		public BloqueContext bloque(int i) {
			return getRuleContext(BloqueContext.class,i);
		}
		public TerminalNode SINO() { return getToken(ExpresionesParser.SINO, 0); }
		public InstrIfContext(InstruccionesContext ctx) { copyFrom(ctx); }
	}

	public final InstruccionesContext instrucciones() throws RecognitionException {
		InstruccionesContext _localctx = new InstruccionesContext(_ctx, getState());
		enterRule(_localctx, 2, RULE_instrucciones);
		int _la;
		try {
			setState(39);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case TIPO:
				_localctx = new InstrDeclContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(24);
				declaracion();
				setState(25);
				match(PUNTO_COMA);
				}
				break;
			case ID:
				_localctx = new InstrAsigContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(27);
				asignacion();
				setState(28);
				match(PUNTO_COMA);
				}
				break;
			case SI:
				_localctx = new InstrIfContext(_localctx);
				enterOuterAlt(_localctx, 3);
				{
				setState(30);
				match(SI);
				setState(31);
				match(PAR_IZQ);
				setState(32);
				condicion(0);
				setState(33);
				match(PAR_DER);
				setState(34);
				bloque();
				setState(37);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==SINO) {
					{
					setState(35);
					match(SINO);
					setState(36);
					bloque();
					}
				}

				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class BloqueContext extends ParserRuleContext {
		public TerminalNode LLAVE_IZQ() { return getToken(ExpresionesParser.LLAVE_IZQ, 0); }
		public TerminalNode LLAVE_DER() { return getToken(ExpresionesParser.LLAVE_DER, 0); }
		public List<InstruccionesContext> instrucciones() {
			return getRuleContexts(InstruccionesContext.class);
		}
		public InstruccionesContext instrucciones(int i) {
			return getRuleContext(InstruccionesContext.class,i);
		}
		public BloqueContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_bloque; }
	}

	public final BloqueContext bloque() throws RecognitionException {
		BloqueContext _localctx = new BloqueContext(_ctx, getState());
		enterRule(_localctx, 4, RULE_bloque);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(41);
			match(LLAVE_IZQ);
			setState(45);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & 16777236L) != 0)) {
				{
				{
				setState(42);
				instrucciones();
				}
				}
				setState(47);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(48);
			match(LLAVE_DER);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class DeclaracionContext extends ParserRuleContext {
		public TerminalNode TIPO() { return getToken(ExpresionesParser.TIPO, 0); }
		public TerminalNode ID() { return getToken(ExpresionesParser.ID, 0); }
		public TerminalNode ASIGNACION() { return getToken(ExpresionesParser.ASIGNACION, 0); }
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
		}
		public DeclaracionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_declaracion; }
	}

	public final DeclaracionContext declaracion() throws RecognitionException {
		DeclaracionContext _localctx = new DeclaracionContext(_ctx, getState());
		enterRule(_localctx, 6, RULE_declaracion);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(50);
			match(TIPO);
			setState(51);
			match(ID);
			setState(54);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==ASIGNACION) {
				{
				setState(52);
				match(ASIGNACION);
				setState(53);
				expr(0);
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class AsignacionContext extends ParserRuleContext {
		public TerminalNode ID() { return getToken(ExpresionesParser.ID, 0); }
		public TerminalNode ASIGNACION() { return getToken(ExpresionesParser.ASIGNACION, 0); }
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
		}
		public AsignacionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_asignacion; }
	}

	public final AsignacionContext asignacion() throws RecognitionException {
		AsignacionContext _localctx = new AsignacionContext(_ctx, getState());
		enterRule(_localctx, 8, RULE_asignacion);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(56);
			match(ID);
			setState(57);
			match(ASIGNACION);
			setState(58);
			expr(0);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class CondicionContext extends ParserRuleContext {
		public CondicionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_condicion; }
	 
		public CondicionContext() { }
		public void copyFrom(CondicionContext ctx) {
			super.copyFrom(ctx);
		}
	}
	@SuppressWarnings("CheckReturnValue")
	public static class RelacionalContext extends CondicionContext {
		public Token op;
		public List<ExprContext> expr() {
			return getRuleContexts(ExprContext.class);
		}
		public ExprContext expr(int i) {
			return getRuleContext(ExprContext.class,i);
		}
		public TerminalNode MAYOR() { return getToken(ExpresionesParser.MAYOR, 0); }
		public TerminalNode MENOR() { return getToken(ExpresionesParser.MENOR, 0); }
		public TerminalNode IGUAL() { return getToken(ExpresionesParser.IGUAL, 0); }
		public TerminalNode MAYOR_IGUAL() { return getToken(ExpresionesParser.MAYOR_IGUAL, 0); }
		public TerminalNode MENOR_IGUAL() { return getToken(ExpresionesParser.MENOR_IGUAL, 0); }
		public TerminalNode DIFERENTE() { return getToken(ExpresionesParser.DIFERENTE, 0); }
		public RelacionalContext(CondicionContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class ParentesisCondContext extends CondicionContext {
		public TerminalNode PAR_IZQ() { return getToken(ExpresionesParser.PAR_IZQ, 0); }
		public CondicionContext condicion() {
			return getRuleContext(CondicionContext.class,0);
		}
		public TerminalNode PAR_DER() { return getToken(ExpresionesParser.PAR_DER, 0); }
		public ParentesisCondContext(CondicionContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class NotLogicaContext extends CondicionContext {
		public TerminalNode NO_LOGICO() { return getToken(ExpresionesParser.NO_LOGICO, 0); }
		public CondicionContext condicion() {
			return getRuleContext(CondicionContext.class,0);
		}
		public NotLogicaContext(CondicionContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class LogicaContext extends CondicionContext {
		public List<CondicionContext> condicion() {
			return getRuleContexts(CondicionContext.class);
		}
		public CondicionContext condicion(int i) {
			return getRuleContext(CondicionContext.class,i);
		}
		public TerminalNode O_LOGICO() { return getToken(ExpresionesParser.O_LOGICO, 0); }
		public TerminalNode Y_LOGICO() { return getToken(ExpresionesParser.Y_LOGICO, 0); }
		public LogicaContext(CondicionContext ctx) { copyFrom(ctx); }
	}

	public final CondicionContext condicion() throws RecognitionException {
		return condicion(0);
	}

	private CondicionContext condicion(int _p) throws RecognitionException {
		ParserRuleContext _parentctx = _ctx;
		int _parentState = getState();
		CondicionContext _localctx = new CondicionContext(_ctx, _parentState);
		CondicionContext _prevctx = _localctx;
		int _startState = 10;
		enterRecursionRule(_localctx, 10, RULE_condicion, _p);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(71);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,5,_ctx) ) {
			case 1:
				{
				_localctx = new NotLogicaContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;

				setState(61);
				match(NO_LOGICO);
				setState(62);
				condicion(3);
				}
				break;
			case 2:
				{
				_localctx = new RelacionalContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(63);
				expr(0);
				setState(64);
				((RelacionalContext)_localctx).op = _input.LT(1);
				_la = _input.LA(1);
				if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & 2064384L) != 0)) ) {
					((RelacionalContext)_localctx).op = (Token)_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				setState(65);
				expr(0);
				}
				break;
			case 3:
				{
				_localctx = new ParentesisCondContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(67);
				match(PAR_IZQ);
				setState(68);
				condicion(0);
				setState(69);
				match(PAR_DER);
				}
				break;
			}
			_ctx.stop = _input.LT(-1);
			setState(81);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,7,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					if ( _parseListeners!=null ) triggerExitRuleEvent();
					_prevctx = _localctx;
					{
					setState(79);
					_errHandler.sync(this);
					switch ( getInterpreter().adaptivePredict(_input,6,_ctx) ) {
					case 1:
						{
						_localctx = new LogicaContext(new CondicionContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_condicion);
						setState(73);
						if (!(precpred(_ctx, 5))) throw new FailedPredicateException(this, "precpred(_ctx, 5)");
						setState(74);
						match(O_LOGICO);
						setState(75);
						condicion(6);
						}
						break;
					case 2:
						{
						_localctx = new LogicaContext(new CondicionContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_condicion);
						setState(76);
						if (!(precpred(_ctx, 4))) throw new FailedPredicateException(this, "precpred(_ctx, 4)");
						setState(77);
						match(Y_LOGICO);
						setState(78);
						condicion(5);
						}
						break;
					}
					} 
				}
				setState(83);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,7,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			unrollRecursionContexts(_parentctx);
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ExprContext extends ParserRuleContext {
		public ExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_expr; }
	 
		public ExprContext() { }
		public void copyFrom(ExprContext ctx) {
			super.copyFrom(ctx);
		}
	}
	@SuppressWarnings("CheckReturnValue")
	public static class NumeroContext extends ExprContext {
		public TerminalNode NUMERO() { return getToken(ExpresionesParser.NUMERO, 0); }
		public NumeroContext(ExprContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class VariableContext extends ExprContext {
		public TerminalNode ID() { return getToken(ExpresionesParser.ID, 0); }
		public VariableContext(ExprContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class AritmeticaContext extends ExprContext {
		public List<ExprContext> expr() {
			return getRuleContexts(ExprContext.class);
		}
		public ExprContext expr(int i) {
			return getRuleContext(ExprContext.class,i);
		}
		public TerminalNode MULT() { return getToken(ExpresionesParser.MULT, 0); }
		public TerminalNode DIV() { return getToken(ExpresionesParser.DIV, 0); }
		public TerminalNode SUMA() { return getToken(ExpresionesParser.SUMA, 0); }
		public TerminalNode RESTA() { return getToken(ExpresionesParser.RESTA, 0); }
		public AritmeticaContext(ExprContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class ParentesisExprContext extends ExprContext {
		public TerminalNode PAR_IZQ() { return getToken(ExpresionesParser.PAR_IZQ, 0); }
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
		}
		public TerminalNode PAR_DER() { return getToken(ExpresionesParser.PAR_DER, 0); }
		public ParentesisExprContext(ExprContext ctx) { copyFrom(ctx); }
	}

	public final ExprContext expr() throws RecognitionException {
		return expr(0);
	}

	private ExprContext expr(int _p) throws RecognitionException {
		ParserRuleContext _parentctx = _ctx;
		int _parentState = getState();
		ExprContext _localctx = new ExprContext(_ctx, _parentState);
		ExprContext _prevctx = _localctx;
		int _startState = 12;
		enterRecursionRule(_localctx, 12, RULE_expr, _p);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(91);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case NUMERO:
				{
				_localctx = new NumeroContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;

				setState(85);
				match(NUMERO);
				}
				break;
			case ID:
				{
				_localctx = new VariableContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(86);
				match(ID);
				}
				break;
			case PAR_IZQ:
				{
				_localctx = new ParentesisExprContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(87);
				match(PAR_IZQ);
				setState(88);
				expr(0);
				setState(89);
				match(PAR_DER);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
			_ctx.stop = _input.LT(-1);
			setState(101);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,10,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					if ( _parseListeners!=null ) triggerExitRuleEvent();
					_prevctx = _localctx;
					{
					setState(99);
					_errHandler.sync(this);
					switch ( getInterpreter().adaptivePredict(_input,9,_ctx) ) {
					case 1:
						{
						_localctx = new AritmeticaContext(new ExprContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_expr);
						setState(93);
						if (!(precpred(_ctx, 5))) throw new FailedPredicateException(this, "precpred(_ctx, 5)");
						setState(94);
						_la = _input.LA(1);
						if ( !(_la==MULT || _la==DIV) ) {
						_errHandler.recoverInline(this);
						}
						else {
							if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
							_errHandler.reportMatch(this);
							consume();
						}
						setState(95);
						expr(6);
						}
						break;
					case 2:
						{
						_localctx = new AritmeticaContext(new ExprContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_expr);
						setState(96);
						if (!(precpred(_ctx, 4))) throw new FailedPredicateException(this, "precpred(_ctx, 4)");
						setState(97);
						_la = _input.LA(1);
						if ( !(_la==SUMA || _la==RESTA) ) {
						_errHandler.recoverInline(this);
						}
						else {
							if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
							_errHandler.reportMatch(this);
							consume();
						}
						setState(98);
						expr(5);
						}
						break;
					}
					} 
				}
				setState(103);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,10,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			unrollRecursionContexts(_parentctx);
		}
		return _localctx;
	}

	public boolean sempred(RuleContext _localctx, int ruleIndex, int predIndex) {
		switch (ruleIndex) {
		case 5:
			return condicion_sempred((CondicionContext)_localctx, predIndex);
		case 6:
			return expr_sempred((ExprContext)_localctx, predIndex);
		}
		return true;
	}
	private boolean condicion_sempred(CondicionContext _localctx, int predIndex) {
		switch (predIndex) {
		case 0:
			return precpred(_ctx, 5);
		case 1:
			return precpred(_ctx, 4);
		}
		return true;
	}
	private boolean expr_sempred(ExprContext _localctx, int predIndex) {
		switch (predIndex) {
		case 2:
			return precpred(_ctx, 5);
		case 3:
			return precpred(_ctx, 4);
		}
		return true;
	}

	public static final String _serializedATN =
		"\u0004\u0001\u001bi\u0002\u0000\u0007\u0000\u0002\u0001\u0007\u0001\u0002"+
		"\u0002\u0007\u0002\u0002\u0003\u0007\u0003\u0002\u0004\u0007\u0004\u0002"+
		"\u0005\u0007\u0005\u0002\u0006\u0007\u0006\u0001\u0000\u0001\u0000\u0001"+
		"\u0000\u0004\u0000\u0012\b\u0000\u000b\u0000\f\u0000\u0013\u0001\u0000"+
		"\u0001\u0000\u0001\u0000\u0001\u0001\u0001\u0001\u0001\u0001\u0001\u0001"+
		"\u0001\u0001\u0001\u0001\u0001\u0001\u0001\u0001\u0001\u0001\u0001\u0001"+
		"\u0001\u0001\u0001\u0001\u0001\u0001\u0003\u0001&\b\u0001\u0003\u0001"+
		"(\b\u0001\u0001\u0002\u0001\u0002\u0005\u0002,\b\u0002\n\u0002\f\u0002"+
		"/\t\u0002\u0001\u0002\u0001\u0002\u0001\u0003\u0001\u0003\u0001\u0003"+
		"\u0001\u0003\u0003\u00037\b\u0003\u0001\u0004\u0001\u0004\u0001\u0004"+
		"\u0001\u0004\u0001\u0005\u0001\u0005\u0001\u0005\u0001\u0005\u0001\u0005"+
		"\u0001\u0005\u0001\u0005\u0001\u0005\u0001\u0005\u0001\u0005\u0001\u0005"+
		"\u0003\u0005H\b\u0005\u0001\u0005\u0001\u0005\u0001\u0005\u0001\u0005"+
		"\u0001\u0005\u0001\u0005\u0005\u0005P\b\u0005\n\u0005\f\u0005S\t\u0005"+
		"\u0001\u0006\u0001\u0006\u0001\u0006\u0001\u0006\u0001\u0006\u0001\u0006"+
		"\u0001\u0006\u0003\u0006\\\b\u0006\u0001\u0006\u0001\u0006\u0001\u0006"+
		"\u0001\u0006\u0001\u0006\u0001\u0006\u0005\u0006d\b\u0006\n\u0006\f\u0006"+
		"g\t\u0006\u0001\u0006\u0000\u0002\n\f\u0007\u0000\u0002\u0004\u0006\b"+
		"\n\f\u0000\u0003\u0001\u0000\u000f\u0014\u0001\u0000\r\u000e\u0001\u0000"+
		"\u000b\fo\u0000\u000e\u0001\u0000\u0000\u0000\u0002\'\u0001\u0000\u0000"+
		"\u0000\u0004)\u0001\u0000\u0000\u0000\u00062\u0001\u0000\u0000\u0000\b"+
		"8\u0001\u0000\u0000\u0000\nG\u0001\u0000\u0000\u0000\f[\u0001\u0000\u0000"+
		"\u0000\u000e\u000f\u0005\u0001\u0000\u0000\u000f\u0011\u0005\u0005\u0000"+
		"\u0000\u0010\u0012\u0003\u0002\u0001\u0000\u0011\u0010\u0001\u0000\u0000"+
		"\u0000\u0012\u0013\u0001\u0000\u0000\u0000\u0013\u0011\u0001\u0000\u0000"+
		"\u0000\u0013\u0014\u0001\u0000\u0000\u0000\u0014\u0015\u0001\u0000\u0000"+
		"\u0000\u0015\u0016\u0005\u0006\u0000\u0000\u0016\u0017\u0005\u0000\u0000"+
		"\u0001\u0017\u0001\u0001\u0000\u0000\u0000\u0018\u0019\u0003\u0006\u0003"+
		"\u0000\u0019\u001a\u0005\t\u0000\u0000\u001a(\u0001\u0000\u0000\u0000"+
		"\u001b\u001c\u0003\b\u0004\u0000\u001c\u001d\u0005\t\u0000\u0000\u001d"+
		"(\u0001\u0000\u0000\u0000\u001e\u001f\u0005\u0002\u0000\u0000\u001f \u0005"+
		"\u0007\u0000\u0000 !\u0003\n\u0005\u0000!\"\u0005\b\u0000\u0000\"%\u0003"+
		"\u0004\u0002\u0000#$\u0005\u0003\u0000\u0000$&\u0003\u0004\u0002\u0000"+
		"%#\u0001\u0000\u0000\u0000%&\u0001\u0000\u0000\u0000&(\u0001\u0000\u0000"+
		"\u0000\'\u0018\u0001\u0000\u0000\u0000\'\u001b\u0001\u0000\u0000\u0000"+
		"\'\u001e\u0001\u0000\u0000\u0000(\u0003\u0001\u0000\u0000\u0000)-\u0005"+
		"\u0005\u0000\u0000*,\u0003\u0002\u0001\u0000+*\u0001\u0000\u0000\u0000"+
		",/\u0001\u0000\u0000\u0000-+\u0001\u0000\u0000\u0000-.\u0001\u0000\u0000"+
		"\u0000.0\u0001\u0000\u0000\u0000/-\u0001\u0000\u0000\u000001\u0005\u0006"+
		"\u0000\u00001\u0005\u0001\u0000\u0000\u000023\u0005\u0004\u0000\u0000"+
		"36\u0005\u0018\u0000\u000045\u0005\n\u0000\u000057\u0003\f\u0006\u0000"+
		"64\u0001\u0000\u0000\u000067\u0001\u0000\u0000\u00007\u0007\u0001\u0000"+
		"\u0000\u000089\u0005\u0018\u0000\u00009:\u0005\n\u0000\u0000:;\u0003\f"+
		"\u0006\u0000;\t\u0001\u0000\u0000\u0000<=\u0006\u0005\uffff\uffff\u0000"+
		"=>\u0005\u0017\u0000\u0000>H\u0003\n\u0005\u0003?@\u0003\f\u0006\u0000"+
		"@A\u0007\u0000\u0000\u0000AB\u0003\f\u0006\u0000BH\u0001\u0000\u0000\u0000"+
		"CD\u0005\u0007\u0000\u0000DE\u0003\n\u0005\u0000EF\u0005\b\u0000\u0000"+
		"FH\u0001\u0000\u0000\u0000G<\u0001\u0000\u0000\u0000G?\u0001\u0000\u0000"+
		"\u0000GC\u0001\u0000\u0000\u0000HQ\u0001\u0000\u0000\u0000IJ\n\u0005\u0000"+
		"\u0000JK\u0005\u0016\u0000\u0000KP\u0003\n\u0005\u0006LM\n\u0004\u0000"+
		"\u0000MN\u0005\u0015\u0000\u0000NP\u0003\n\u0005\u0005OI\u0001\u0000\u0000"+
		"\u0000OL\u0001\u0000\u0000\u0000PS\u0001\u0000\u0000\u0000QO\u0001\u0000"+
		"\u0000\u0000QR\u0001\u0000\u0000\u0000R\u000b\u0001\u0000\u0000\u0000"+
		"SQ\u0001\u0000\u0000\u0000TU\u0006\u0006\uffff\uffff\u0000U\\\u0005\u0019"+
		"\u0000\u0000V\\\u0005\u0018\u0000\u0000WX\u0005\u0007\u0000\u0000XY\u0003"+
		"\f\u0006\u0000YZ\u0005\b\u0000\u0000Z\\\u0001\u0000\u0000\u0000[T\u0001"+
		"\u0000\u0000\u0000[V\u0001\u0000\u0000\u0000[W\u0001\u0000\u0000\u0000"+
		"\\e\u0001\u0000\u0000\u0000]^\n\u0005\u0000\u0000^_\u0007\u0001\u0000"+
		"\u0000_d\u0003\f\u0006\u0006`a\n\u0004\u0000\u0000ab\u0007\u0002\u0000"+
		"\u0000bd\u0003\f\u0006\u0005c]\u0001\u0000\u0000\u0000c`\u0001\u0000\u0000"+
		"\u0000dg\u0001\u0000\u0000\u0000ec\u0001\u0000\u0000\u0000ef\u0001\u0000"+
		"\u0000\u0000f\r\u0001\u0000\u0000\u0000ge\u0001\u0000\u0000\u0000\u000b"+
		"\u0013%\'-6GOQ[ce";
	public static final ATN _ATN =
		new ATNDeserializer().deserialize(_serializedATN.toCharArray());
	static {
		_decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
		for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
			_decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
		}
	}
}