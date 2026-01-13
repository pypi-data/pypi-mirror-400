
// Enum para representar os tipos de token
enum TokenType {
    VARIABLE,
    OPERATOR,
    PARENTHESIS
};

// Estrutura para um token
struct Token {
    std::string value;
    TokenType type;
};

class RuleCompiler {
public:
    // Construtor
    RuleCompiler() {}
    
    // Compila uma regra booleana e retorna todas as combinações que a tornam verdadeira
    std::vector<std::vector<int>> compileRule(const std::string& rule, const std::map<std::string, int>& variableIndexes);
    
private:
    // Função para verificar se um caractere é parte de um nome de variável
    bool isVariableChar(char c);
    
    // Tokeniza a string de expressão
    std::vector<Token> tokenize(const std::string& expression);
    
    // Precedência dos operadores
    int precedence(const std::string& op);
    
    // Converte a lista de tokens para notação pós-fixa (RPN)
    std::vector<Token> infixToPostfix(const std::vector<Token>& infixTokens);
    
    // Avalia a expressão em notação pós-fixa
    bool evaluatePostfix(const std::vector<Token>& postfixTokens, const std::map<std::string, bool>& values);
    
    // Gera todas as combinações possíveis de valores para as variáveis
    std::vector<std::map<std::string, bool>> generateAllCombinations(const std::vector<std::string>& variables);
};

bool RuleCompiler::isVariableChar(char c) {
    return isalnum(c) || c == '_';
}

std::vector<Token> RuleCompiler::tokenize(const std::string& expression) {
    std::vector<Token> tokens;
    for (size_t i = 0; i < expression.length(); ) {
        char c = expression[i];
        if (isspace(c)) {
            i++;
            continue;
        }

        if (c == '+' || c == '*' || c == '!') {
            tokens.push_back({std::string(1, c), OPERATOR});
            i++;
        } else if (c == '(' || c == ')') {
            tokens.push_back({std::string(1, c), PARENTHESIS});
            i++;
        } else if (isalpha(c) || c == '_') {
            std::string varName = "";
            while (i < expression.length() && isVariableChar(expression[i])) {
                varName += expression[i];
                i++;
            }
            tokens.push_back({varName, VARIABLE});
        } else {
            // Caractere desconhecido
            throw Exception(("Caractere invalido na expressao: " + std::string(1, c)).c_str());
        }
    }
    return tokens;
}

int RuleCompiler::precedence(const std::string& op) {
    if (op == "!") return 3;
    if (op == "*") return 2;
    if (op == "+") return 1;
    return 0;
}

std::vector<Token> RuleCompiler::infixToPostfix(const std::vector<Token>& infixTokens) {
    std::vector<Token> postfixTokens;
    std::stack<Token> opStack;

    for (const auto& token : infixTokens) {
        if (token.type == VARIABLE) {
            postfixTokens.push_back(token);
        } else if (token.value == "(") {
            opStack.push(token);
        } else if (token.value == ")") {
            while (!opStack.empty() && opStack.top().value != "(") {
                postfixTokens.push_back(opStack.top());
                opStack.pop();
            }
            if (!opStack.empty()) opStack.pop(); // Remove o '('
        } else if (token.type == OPERATOR) {
            while (!opStack.empty() && opStack.top().type == OPERATOR && precedence(opStack.top().value) >= precedence(token.value)) {
                postfixTokens.push_back(opStack.top());
                opStack.pop();
            }
            opStack.push(token);
        }
    }

    while (!opStack.empty()) {
        postfixTokens.push_back(opStack.top());
        opStack.pop();
    }
    return postfixTokens;
}

bool RuleCompiler::evaluatePostfix(const std::vector<Token>& postfixTokens, const std::map<std::string, bool>& values) {
    std::stack<bool> operandStack;

    for (const auto& token : postfixTokens) {
        if (token.type == VARIABLE) {
            if (values.count(token.value)) {
                operandStack.push(values.at(token.value));
            } else {
                throw Exception(("Variavel nao encontrada: " + token.value).c_str());
            }
        } else if (token.value == "!") {
            if (operandStack.empty()) { 
                throw Exception("Erro de expressao (NOT)."); 
            }
            bool val = operandStack.top();
            operandStack.pop();
            operandStack.push(!val);
        } else if (token.value == "*" || token.value == "+") {
            if (operandStack.size() < 2) { 
                throw Exception(("Erro de expressao (" + token.value + ").").c_str()); 
            }
            bool right = operandStack.top();
            operandStack.pop();
            bool left = operandStack.top();
            operandStack.pop();

            if (token.value == "*") { // AND
                operandStack.push(left && right);
            } else { // OR
                operandStack.push(left || right);
            }
        }
    }

    if (operandStack.size() != 1) { 
        throw Exception("Erro de expressao final."); 
    }
    return operandStack.top();
}

std::vector<std::map<std::string, bool>> RuleCompiler::generateAllCombinations(const std::vector<std::string>& variables) {
    std::vector<std::map<std::string, bool>> combinations;
    int numVariables = variables.size();
    int numCombinations = 1 << numVariables;

    for (int i = 0; i < numCombinations; ++i) {
        std::map<std::string, bool> combination;
        for (int j = 0; j < numVariables; ++j) {
            bool value = (i >> j) & 1;
            combination[variables[j]] = value;
        }
        combinations.push_back(combination);
    }
    return combinations;
}

std::vector<std::vector<int>> RuleCompiler::compileRule(const std::string& rule, const std::map<std::string, int>& variableIndexes) {
    // Etapa 1: Tokenização
    std::vector<Token> infixTokens = tokenize(rule);

    // Etapa 2: Encontrar as variáveis na regra
    std::vector<std::string> variables;
    for (const auto& token : infixTokens) {
        if (token.type == VARIABLE) {
            bool found = false;
            for(const auto& var : variables) {
                if(var == token.value) {
                    found = true;
                    break;
                }
            }
            if(!found) {
                // Verificar se a variável existe no variableIndexes
                if (variableIndexes.find(token.value) == variableIndexes.end()) {
                    throw Exception(("Variavel '" + token.value + "' nao encontrada no variableIndexes").c_str());
                }
                variables.push_back(token.value);
            }
        }
    }
    std::sort(variables.begin(), variables.end());

    // Etapa 3: Converter para notação pós-fixa
    std::vector<Token> postfixTokens = infixToPostfix(infixTokens);

    // Etapa 4: Gerar todas as combinações
    std::vector<std::map<std::string, bool>> allCombinations = generateAllCombinations(variables);

    // Etapa 5: Avaliar cada combinação e coletar as que tornam a regra verdadeira
    std::vector<std::vector<int>> trueCombinations;
    
    for (const auto& combination : allCombinations) {
        bool result = evaluatePostfix(postfixTokens, combination);
        if (result) {
            // Converter a combinação para o formato esperado pelo WiSARD
            // Ordenar as variáveis pela ordem dos índices
            std::vector<std::pair<std::string, int>> sortedVars;
            for (const auto& var : variables) {
                sortedVars.push_back({var, variableIndexes.at(var)});
            }
            std::sort(sortedVars.begin(), sortedVars.end(), 
                [](const std::pair<std::string, int>& a, const std::pair<std::string, int>& b) {
                    return a.second < b.second;
                });
            
            std::vector<int> ruleValues;
            for (const auto& varPair : sortedVars) {
                ruleValues.push_back(combination.at(varPair.first) ? 1 : 0);
            }
            trueCombinations.push_back(ruleValues);
        }
    }

    return trueCombinations;
}

class Wisard{
public:
  Wisard(int addressSize): Wisard(addressSize, {}){}
  Wisard(int addressSize, nl::json c): addressSize(addressSize){
    srand(randint(0,1000000));
    nl::json value;

    value = c["bleachingActivated"];
    bleachingActivated = value.is_null() ? true : value.get<bool>();

    value = c["verbose"];
    verbose = value.is_null() ? false : value.get<bool>();

    value = c["ignoreZero"];
    ignoreZero = value.is_null() ? false : value.get<bool>();

    value = c["completeAddressing"];
    completeAddressing = value.is_null() ? true : value.get<bool>();

    value = c["mapping"];
    mapping = value.is_null() ? std::map<std::string, std::vector<std::vector<int>>>() : value.get<std::map<std::string, std::vector<std::vector<int>>>>();

    value = c["indexes"];
    indexes = value.is_null() ? std::vector<int>(0) : value.get<std::vector<int>>();

    value = c["base"];
    base = value.is_null() ? 2 : value.get<int>();

    value = c["confidence"];
    confidence = value.is_null() ? 1 : value.get<int>();

    value = c["searchBestConfidence"];
    searchBestConfidence = value.is_null() ? false : value.get<bool>();

    value = c["returnConfidence"];
    returnConfidence = value.is_null() ? false : value.get<bool>();

    value = c["returnActivationDegree"];
    returnActivationDegree = value.is_null() ? false : value.get<bool>();

    value = c["returnClassesDegrees"];
    returnClassesDegrees = value.is_null() ? false : value.get<bool>();
  }

  Wisard(std::string config):Wisard(0,nl::json::parse(config)){
    nl::json c = nl::json::parse(config);
    addressSize=c["addressSize"];

    nl::json classes = c["classes"];
    nl::json dConfig = {
      {"ignoreZero", ignoreZero},
      {"base", base}
    };
    for(nl::json::iterator it = classes.begin(); it != classes.end(); ++it){
      nl::json d = it.value();
      d.merge_patch(dConfig);
      discriminators[it.key()] = Discriminator(d);
    }
  }

  long getsizeof(){
    long size = sizeof(Wisard);
    size += sizeof(int)*indexes.size();
    for(std::map<std::string, Discriminator>::iterator d=discriminators.begin(); d!=discriminators.end(); ++d){
      size += d->first.size() + d->second.getsizeof();
    }
    return size;
  }

  ~Wisard(){
    indexes.clear();
    discriminators.clear();
  }

  void train(const DataSet& dataset) {
    int numberOfRAMS = calculateNumberOfRams(dataset[0].size(), addressSize, completeAddressing);
    checkConfidence(numberOfRAMS);
    for(size_t i=0; i<dataset.size(); i++){
      if(verbose) std::cout << "\rtraining " << i+1 << " of " << dataset.size();
      train<BinInput>(dataset[i], dataset.getLabel(i));
    }
  }

  void trainWithRules(const DataSet& dataset) {
    int numberOfRAMS = calculateNumberOfRams(dataset[0].size(), addressSize, completeAddressing);
    checkConfidence(numberOfRAMS);
    for(size_t i=0; i<dataset.size(); i++){
      if(verbose) std::cout << "\rtraining with rules " << i+1 << " of " << dataset.size();
      trainWithRules<BinInput>(dataset[i], dataset.getLabel(i));
    }
  }

  void train(const std::vector<std::vector<int>>& images, const std::vector<std::string>& labels){
    int numberOfRAMS = calculateNumberOfRams(images[0].size(), addressSize, completeAddressing);
    checkConfidence(numberOfRAMS);
    checkInputSizes(images.size(), labels.size());
    for(unsigned int i=0; i<images.size(); i++){
      if(verbose) std::cout << "\rtraining " << i+1 << " of " << images.size();
      train<std::vector<int>>(images[i], labels[i]);
    }
    if(verbose) std::cout << "\r" << std::endl;
  }

  void trainWithRules(const std::vector<std::vector<int>>& images, const std::vector<std::string>& labels){
    int numberOfRAMS = calculateNumberOfRams(images[0].size(), addressSize, completeAddressing);
    checkConfidence(numberOfRAMS);
    checkInputSizes(images.size(), labels.size());
    for(unsigned int i=0; i<images.size(); i++){
      if(verbose) std::cout << "\rtraining with rules " << i+1 << " of " << images.size();
      trainWithRules<std::vector<int>>(images[i], labels[i]);
    }
    if(verbose) std::cout << "\r" << std::endl;
  }

  std::vector<std::string> classify(const std::vector<std::vector<int>>& images){
    return _classify<std::vector<std::vector<int>>>(images);
  }

  std::vector<std::string> classify(const DataSet& images){
    return _classify<DataSet>(images);
  }

  std::vector<std::string> classify_with_rules(const std::vector<std::vector<int>>& images){
    return _classify_with_rules<std::vector<std::vector<int>>>(images);
  }

  std::vector<std::string> classify_with_rules(const DataSet& images){
    return _classify_with_rules<DataSet>(images);
  }

  void leaveOneOut(const std::vector<int>& image, const std::string& label){
    auto d = discriminators.find(label);
    if(d != discriminators.end()){
      d->second.untrain(image);
    }
  }

  void leaveMoreOut(const std::vector<std::vector<int>>& images, const std::vector<std::string>& labels){
    checkInputSizes(images.size(), labels.size());
    for(unsigned int i=0; i<images.size(); i++){
      if(verbose) std::cout << "\runtraining " << i+1 << " of " << images.size();
      leaveOneOut(images[i], labels[i]);
    }
    if(verbose) std::cout << "\r" << std::endl;
  }

  std::map<std::string,std::vector<int>> getMentalImages(){
    std::map<std::string,std::vector<int>> images;
    for(std::map<std::string, Discriminator>::iterator d=discriminators.begin(); d!=discriminators.end(); ++d){
      images[d->first] = d->second.getMentalImage();
    }
    return images;
  }

  std::string getRAMSInfo(){
    std::string info = "WiSARD RAMs Information:\n";
    info += "========================\n";
    for(std::map<std::string, Discriminator>::iterator d=discriminators.begin(); d!=discriminators.end(); ++d){
      info += "Class: " + d->first + "\n";
      info += d->second.getRAMSInfo();
      info += "========================\n";
    }
    return info;
  }

  std::string jsonConfig(){
    nl::json config = getConfig();
    config["classes"] = getConfigClassesJSON();
    return config.dump(2);
  }

  std::string json(bool huge, std::string path) {
    nl::json config = getConfig();
    config["classes"] = getClassesJSON(huge,path);
    return config.dump();
  }
  std::string json(bool huge) {
    return json(huge,"");
  }
  std::string json() {
    return json(false,"");
  }

  void addRule(const std::string& label, const std::vector<int>& variableIndexes, const std::vector<std::vector<int>>& multipleRuleValues, int alpha, int basein = 2, bool ignoreZeroIn = false){
    if(discriminators.find(label) == discriminators.end()){
      // Criar discriminador considerando mapeamento existente se disponível
      int inferredEntrySize = 0;
      if(variableIndexes.size() > 0){
        inferredEntrySize = *std::max_element(variableIndexes.begin(), variableIndexes.end()) + 1;
      }
      // Garantir que entrySize seja pelo menos addressSize
      if(inferredEntrySize < addressSize){
        inferredEntrySize = addressSize;
      }
      
      // Se há mapeamento, usar o tamanho real dos dados baseado no mapeamento
      auto it = mapping.find(label);
      if (it != mapping.end()) {
        // Calcular o tamanho real baseado no mapeamento
        int maxIndexInMapping = 0;
        for (const auto& tuple : it->second) {
          for (int index : tuple) {
            if (index > maxIndexInMapping) {
              maxIndexInMapping = index;
            }
          }
        }
        // O entrySize deve ser pelo menos maxIndexInMapping + 1
        inferredEntrySize = maxIndexInMapping + 1;
      }
      
      // Verificar se existe mapeamento para esta classe
      if (it != mapping.end())
      {
        // Usar mapeamento existente
        discriminators[label] = Discriminator(it->second, inferredEntrySize, ignoreZero, base);
      }
      else
      {
        // Criar discriminador vazio apenas para regras
        // O entrySize será expandido quando trainWithRules() for chamado
        discriminators[label] = Discriminator(inferredEntrySize);
      }
    }
    discriminators[label].addRuleRAM(variableIndexes, multipleRuleValues, alpha, basein, ignoreZeroIn);
  }

  void addRule(const std::string& label, const std::map<std::string, int>& variableIndexes, const std::string& rule, int alpha, int basein = 2, bool ignoreZeroIn = false){
    // Converter map para vector de índices ordenados
    std::vector<std::pair<std::string, int>> sortedVars;
    for (const auto& pair : variableIndexes) {
      sortedVars.push_back(pair);
    }
    std::sort(sortedVars.begin(), sortedVars.end(), 
        [](const std::pair<std::string, int>& a, const std::pair<std::string, int>& b) {
            return a.second < b.second;
        });
    
    std::vector<int> indexes;
    for (const auto& pair : sortedVars) {
      indexes.push_back(pair.second);
    }
    
    RuleCompiler compiler;
    std::vector<std::vector<int>> ruleValues = compiler.compileRule(rule, variableIndexes);

    if(ruleValues.empty()){
      throw Exception("The boolean rule has no valid combinations that make it true! Please check for logical contradictions in the rule.");
    }

    addRule(label, indexes, ruleValues, alpha, basein, ignoreZeroIn);
  }


protected:
  template<typename T>
  void train(const T& image, const std::string& label){
    if(discriminators.find(label) == discriminators.end()){
      makeDiscriminator(label, image.size());
    }
    else {
      // Se o discriminador já existe (pode ter regras), adicionar RAMs normais se necessário
      // Verificar se este discriminador foi criado com mapeamento
      bool hasMapping = mapping.find(label) != mapping.end();
      discriminators[label].ensureNormalRAMs(addressSize, image.size(), ignoreZero, completeAddressing, base, !hasMapping);
    }
    discriminators[label].train(image);
  }

  template<typename T>
  void trainWithRules(const T& image, const std::string& label){
    if(discriminators.find(label) == discriminators.end()){
      // Seguir a mesma lógica da função train: criar discriminador com tamanho da imagem
      makeDiscriminator(label, image.size());
    }
    else {
      // Se o discriminador já existe (pode ter regras), expandir entrySize se necessário
      if(discriminators[label].getEntrySize() < image.size()){
        discriminators[label].expandEntrySize(image.size());
      }
      // Adicionar RAMs normais se necessário
      // Verificar se este discriminador foi criado com mapeamento
      bool hasMapping = mapping.find(label) != mapping.end();
      if(!hasMapping){
        // Se não há mapeamento, sempre criar RAMs normais
        discriminators[label].ensureNormalRAMs(addressSize, image.size(), ignoreZero, completeAddressing, base, true);
      }
      else {
        // Se há mapeamento, não criar RAMs normais (elas já existem)
        discriminators[label].ensureNormalRAMs(addressSize, image.size(), ignoreZero, completeAddressing, base, false);
      }
    }

    discriminators[label].trainWithRules(image);
  }

  template<typename T>
  std::vector<std::string> _classify(const T& images){
    //float numberOfRAMS = calculateNumberOfRams(images[0].size(), addressSize, completeAddressing);
    std::vector<std::string> labels(images.size());

    for(unsigned int i=0; i<images.size(); i++){
      if(verbose) std::cout << "\rclassifying " << i+1 << " of " << images.size();
      std::map<std::string,int> candidates = classify(images[i],searchBestConfidence);
      labels[i] = Bleaching::getBiggestCandidate(candidates);
    }
    if(verbose) std::cout << "\r" << std::endl;
    return labels;
  }

  template<typename T>
  std::vector<std::string> _classify_with_rules(const T& images){
    std::vector<std::string> labels(images.size());

    for(unsigned int i=0; i<images.size(); i++){
      if(verbose) std::cout << "\rclassifying with rules " << i+1 << " of " << images.size();
      std::map<std::string,int> candidates = classify_with_rules_single(images[i], searchBestConfidence);
      
      if(verbose) {
        std::cout << "\n=== DEBUG: Classificação da imagem " << i+1 << " ===" << std::endl;
        std::cout << "Imagem: [";
        for(size_t j=0; j<images[i].size(); j++){
          std::cout << images[i][j];
          if(j < images[i].size()-1) std::cout << ", ";
        }
        std::cout << "]" << std::endl;
        
        // Mostrar votações de cada discriminador
        for(auto& candidate : candidates){
          std::cout << "Discriminador '" << candidate.first << "': " << candidate.second << " votos" << std::endl;
        }
        
        std::string winner = Bleaching::getBiggestCandidate(candidates);
        std::cout << "Classe vencedora: " << winner << std::endl;
        std::cout << "=================================" << std::endl;
      }
      
      labels[i] = Bleaching::getBiggestCandidate(candidates);
    }
    if(verbose) std::cout << "\r" << std::endl;
    return labels;
  }

  std::map<std::string, int> classify(const std::vector<int>& image, bool searchBestConfidence=false){
    return __classify<std::vector<int>>(image,searchBestConfidence);
  }

  std::map<std::string, int> classify(const BinInput& image, bool searchBestConfidence=false){
    return __classify<BinInput>(image,searchBestConfidence);
  }

  std::map<std::string, int> classify_with_rules_single(const std::vector<int>& image, bool searchBestConfidence=false){
    return __classify_with_rules<std::vector<int>>(image, searchBestConfidence);
  }

  std::map<std::string, int> classify_with_rules_single(const BinInput& image, bool searchBestConfidence=false){
    return __classify_with_rules<BinInput>(image, searchBestConfidence);
  }

  template<typename T>
  std::map<std::string, int> __classify(const T& image, bool searchBestConfidence=false){
    std::map<std::string,std::vector<int>> allvotes;

    for(std::map<std::string,Discriminator>::iterator i=discriminators.begin(); i!=discriminators.end(); ++i){
      allvotes[i->first] = i->second.classify(image);
    }
    return Bleaching::make(allvotes, bleachingActivated, searchBestConfidence, confidence);
  }

  template<typename T>
  std::map<std::string, int> __classify_with_rules(const T& image, bool searchBestConfidence=false){
    std::map<std::string,std::vector<int>> allvotes;
    std::map<std::string,std::vector<bool>> ruleRAMs;

    for(std::map<std::string,Discriminator>::iterator i=discriminators.begin(); i!=discriminators.end(); ++i){
      allvotes[i->first] = i->second.classify_with_rules(image);
      ruleRAMs[i->first] = i->second.getRuleRAMsInfo();
      
      if(verbose) {
        std::cout << "  Discriminador '" << i->first << "':" << std::endl;
        std::vector<int> votes = allvotes[i->first];
        int total_votes = 0;
        for(size_t j=0; j<votes.size(); j++){
          std::cout << "    RAM " << j << ": " << votes[j] << " votos" << std::endl;
          total_votes += votes[j];
        }
        std::cout << "    Total: " << total_votes << " votos" << std::endl;
      }
    }
    
    if(searchBestConfidence){
      // Para searchBestConfidence, usar a função normal por enquanto
      return Bleaching::make(allvotes, bleachingActivated, searchBestConfidence, confidence);
    }
    else{
      // Usar a nova função que trata RAMs de regra de forma diferente
      return Bleaching::makeConfidencelessWithRules(allvotes, ruleRAMs, bleachingActivated, confidence);
    }
  }

  nl::json getClassesJSON(bool huge, std::string path){
    nl::json c;
    for(std::map<std::string, Discriminator>::iterator d=discriminators.begin(); d!=discriminators.end(); ++d){
      c[d->first] = d->second.getJSON(huge,path+(d->first)+"__");
    }
    return c;
  }

  nl::json getConfigClassesJSON(){
    nl::json c;
    for(std::map<std::string, Discriminator>::iterator d=discriminators.begin(); d!=discriminators.end(); ++d){
      c[d->first] = d->second.getConfigJSON();
    }
    return c;
  }

  nl::json getConfig(){
    nl::json config = {
      {"version", __version__},
      {"addressSize", addressSize},
      {"bleachingActivated", bleachingActivated},
      {"verbose", verbose},
      {"indexes", indexes},
      {"ignoreZero", ignoreZero},
      {"completeAddressing", completeAddressing},
      {"base", base},
      {"confidence", confidence},
      // {"searchBestConfidence", searchBestConfidence},
      {"returnConfidence", returnConfidence},
      {"returnActivationDegree", returnActivationDegree},
      {"returnClassesDegrees", returnClassesDegrees}
    };
    return config;
  }

  void makeDiscriminator(std::string label, int entrySize){
    auto it = mapping.find(label);
    if (it != mapping.end())
    {
      discriminators[label] = Discriminator(it->second, entrySize, ignoreZero, base);
    }
    else
    {
      // Sempre usar setRAMShuffle com completeAddressing para garantir mapeamento correto
      discriminators[label] = Discriminator(addressSize, entrySize, ignoreZero, completeAddressing, base);
    }
  }

  void checkInputSizes(const int imageSize, const int labelsSize){
    if(imageSize != labelsSize){
      throw Exception("The size of data is not the same of the size of labels!");
    }
  }

  void checkConfidence(int numberOfRAMS){
    if(confidence > numberOfRAMS){
      throw Exception("The confidence can not be bigger than number of RAMs!");
    }
  }

  int addressSize;
  bool bleachingActivated;
  bool verbose;
  std::map<std::string, std::vector<std::vector<int>>> mapping;
  std::vector<int> indexes;
  bool ignoreZero;
  bool completeAddressing;
  int base;
  bool searchBestConfidence;
  bool returnConfidence;
  bool returnActivationDegree;
  bool returnClassesDegrees;
  int confidence;
  std::map<std::string, Discriminator> discriminators;
};
