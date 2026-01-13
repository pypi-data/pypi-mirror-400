
class WisardWrapper: public Wisard{
public:
  WisardWrapper(std::string config):Wisard(config){}
  WisardWrapper(int addressSize, py::kwargs kwargs): Wisard(addressSize){

    for(auto arg: kwargs){
      if(std::string(py::str(arg.first)).compare("bleachingActivated") == 0)
        bleachingActivated = arg.second.cast<bool>();

      if(std::string(py::str(arg.first)).compare("verbose") == 0)
        verbose = arg.second.cast<bool>();

      if(std::string(py::str(arg.first)).compare("ignoreZero") == 0)
        ignoreZero = arg.second.cast<bool>();

      if(std::string(py::str(arg.first)).compare("completeAddressing") == 0)
        completeAddressing = arg.second.cast<bool>();

      if (std::string(py::str(arg.first)).compare("mapping") == 0)
        mapping = arg.second.cast<std::map<std::string, std::vector<std::vector<int>>>>();

      if(std::string(py::str(arg.first)).compare("indexes") == 0)
        indexes = arg.second.cast<std::vector<int>>();

      if(std::string(py::str(arg.first)).compare("base") == 0)
        base = arg.second.cast<int>();

      if(std::string(py::str(arg.first)).compare("searchBestConfidence") == 0)
        searchBestConfidence = arg.second.cast<bool>();

      if(std::string(py::str(arg.first)).compare("returnConfidence") == 0)
        returnConfidence = arg.second.cast<bool>();

      if(std::string(py::str(arg.first)).compare("returnActivationDegree") == 0)
        returnActivationDegree = arg.second.cast<bool>();

      if(std::string(py::str(arg.first)).compare("returnClassesDegrees") == 0)
        returnClassesDegrees = arg.second.cast<bool>();

      if(std::string(py::str(arg.first)).compare("confidence") == 0)
        confidence = arg.second.cast<int>();
    }
  }

  void setClassifyOutput(py::list& labels, int i, std::string aClass, float numberOfRAMS, std::map<std::string,int>& candidates){
    if(returnConfidence || returnActivationDegree || returnClassesDegrees){
      labels[i] = py::dict(py::arg("class")=aClass);
    }

    if(returnActivationDegree){
      float activationDegree = candidates[aClass]/numberOfRAMS;
      labels[i]["activationDegree"]=activationDegree;
    }

    if(returnConfidence){
      float confidence = Bleaching::getConfidence(candidates, candidates[aClass]);
      labels[i]["confidence"]=confidence;
    }

    if(returnClassesDegrees){
      labels[i]["classesDegrees"] = getClassesDegrees(candidates);
    }

    if(!returnActivationDegree && !returnConfidence && !returnClassesDegrees){
      labels[i] = aClass;
    }
  }

  py::list pyClassify(const std::vector<std::vector<int>>& images){
    return _pyClassify<std::vector<std::vector<int>>>(images);
  }

  py::list pyClassify(const DataSet& images){
    return _pyClassify<DataSet>(images);
  }

  py::list pyClassifyWithRules(const std::vector<std::vector<int>>& images){
    return _pyClassifyWithRules<std::vector<std::vector<int>>>(images);
  }

  py::list pyClassifyWithRules(const DataSet& images){
    return _pyClassifyWithRules<DataSet>(images);
  }

  void pyTrainWithRules(const std::vector<std::vector<int>>& images, const std::vector<std::string>& labels){
    trainWithRules(images, labels);
  }

  void pyTrainWithRules(const DataSet& dataset){
    trainWithRules(dataset);
  }

  // void add_rule(const std::string& label, const std::vector<int>& variableIndexes, const std::vector<int>& ruleValues, int alpha, int basein = 2, bool ignoreZeroIn = false){
  //   addRule(label, variableIndexes, ruleValues, alpha, basein, ignoreZeroIn);
  // }

  // void add_rule(const std::string& label, const std::vector<int>& variableIndexes, const std::vector<std::vector<int>>& multipleRuleValues, int alpha, int basein = 2, bool ignoreZeroIn = false){
  //   addRule(label, variableIndexes, multipleRuleValues, alpha, basein, ignoreZeroIn);
  // }

  // Nova função add_rule que aceita regras booleanas
  void add_rule(const std::string& label, const std::map<std::string, int>& variableIndexes, const std::string& rule, int alpha, int basein = 2, bool ignoreZeroIn = false){
    addRule(label, variableIndexes, rule, alpha, basein, ignoreZeroIn);
  }

  std::string get_rams_info(){
    return getRAMSInfo();
  }

  void debug_classification(const std::vector<std::vector<int>>& images){
    std::cout << "\n=== DEBUG DETALHADO DA CLASSIFICAÇÃO ===" << std::endl;
    for(unsigned int i=0; i<images.size(); i++){
      std::cout << "\n--- Imagem " << i+1 << " ---" << std::endl;
      std::cout << "Dados: [";
      for(size_t j=0; j<images[i].size(); j++){
        std::cout << images[i][j];
        if(j < images[i].size()-1) std::cout << ", ";
      }
      std::cout << "]" << std::endl;
      
      // Classificar e mostrar detalhes
      std::map<std::string,int> candidates = classify_with_rules_single(images[i], searchBestConfidence);
      std::cout << "Resultado da classificação:" << std::endl;
      for(auto& candidate : candidates){
        std::cout << "  " << candidate.first << ": " << candidate.second << " votos" << std::endl;
      }
    }
    std::cout << "========================================\n" << std::endl;
  }

protected:
  py::list getClassesDegrees(std::map<std::string, int> candidates) const{
    float total = 0;
    int index = 0;
    py::list output(candidates.size());
    for(std::map<std::string, int>::iterator i=candidates.begin(); i!=candidates.end(); ++i) total += i->second;
    if(total == 0) total=1;
    for(std::map<std::string, int>::iterator i=candidates.begin(); i!=candidates.end(); ++i){
      output[index] = py::dict(py::arg("class")=i->first, py::arg("degree")=(i->second/total));
      index++;
    }
    return output;
  }

  template<typename T>
  py::list _pyClassify(const T& images){
    float numberOfRAMS = calculateNumberOfRams(images[0].size(), addressSize, completeAddressing);

    py::list labels(images.size());
    for(unsigned int i=0; i<images.size(); i++){
      if(verbose) std::cout << "\rclassifying " << i+1 << " of " << images.size();
      std::map<std::string,int> candidates = classify(images[i],searchBestConfidence);
      std::string aClass = Bleaching::getBiggestCandidate(candidates);
      setClassifyOutput(labels, i, aClass, numberOfRAMS, candidates);
    }
    if(verbose) std::cout << "\r" << std::endl;
    return labels;
  }

  template<typename T>
  py::list _pyClassifyWithRules(const T& images){
    // Usar a função classify_with_rules da classe Wisard que já tem verbose implementado
    std::vector<std::string> results = classify_with_rules(images);
    
    // Converter para py::list mantendo a compatibilidade com setClassifyOutput
    py::list labels(results.size());
    for(unsigned int i=0; i<results.size(); i++){
      labels[i] = results[i];
    }
    return labels;
  }
};
