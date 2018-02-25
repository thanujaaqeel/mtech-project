package org.apache.storm.mfp.bolt;

import org.apache.storm.task.OutputCollector;
import org.apache.storm.task.TopologyContext;
import org.apache.storm.topology.OutputFieldsDeclarer;
import org.apache.storm.topology.base.BaseWindowedBolt;
import org.apache.storm.tuple.Fields;
import org.apache.storm.tuple.Tuple;
import org.apache.storm.tuple.Values;
import org.apache.storm.windowing.TupleWindow;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;


import com.github.chen0040.fpm.AssocRuleMiner;
import com.github.chen0040.fpm.apriori.Apriori;
import com.github.chen0040.fpm.data.MetaData;
import com.github.chen0040.fpm.data.ItemSets;
import com.github.chen0040.fpm.data.ItemSet;

public class MFPMinerBolt extends BaseWindowedBolt {
    private static final Logger LOG = LoggerFactory.getLogger(MFPMinerBolt.class);

    private OutputCollector collector;
    private AssocRuleMiner ruleMiner;
    private int minimumSupportLevel;

    public MFPMinerBolt(int minimumSupportLevel){
        this.minimumSupportLevel = minimumSupportLevel;
    }

    @Override
    public void prepare(Map stormConf, TopologyContext context, OutputCollector collector) {
        this.collector = collector;
        this.ruleMiner = new Apriori();
        this.ruleMiner.setMinSupportLevel(minimumSupportLevel);
    }

    @Override
    public void execute(TupleWindow inputWindow) {
        findMaximalFrequentPatterns(getTransactions(inputWindow));
    }

    @Override
    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        declarer.declare(new Fields("size", "transactions", "item_sets"));
    }

    private void findMaximalFrequentPatterns(List<List<String>> transactions){
        MetaData metaData = new MetaData(transactions);
        ItemSets mfpItemSets = ruleMiner.findMaxPatterns(transactions, metaData.getUniqueItems());
        emit(transactions, mfpItemSets);
    }

    private void emit(List<List<String>> transactions, ItemSets mfpItemSets){
        int transactionsSize = transactions.size();
        String transactionsString = getTransactionsString(transactions);
        String itemSetsString = getItemSetsAsString(mfpItemSets);

        collector.emit(new Values(transactionsSize, transactionsString, itemSetsString));
    }

    private List<List<String>> getTransactions(TupleWindow tupleWindow){
        List<Tuple> tuplesInWindow = tupleWindow.get();
        List<List<String>> transactions = new ArrayList<>();
        
        for (Tuple tuple : tuplesInWindow) {
            transactions.add(getTransaction(tuple));
        }
        return transactions;
    }

    private String getTransactionsString(List<List<String>> transactions){
        StringBuilder builder = new StringBuilder();

        for(List<String> transaction : transactions){
          builder.append(String.join(" ", transaction));
        }
        return builder.toString();
    }

    private String getItemSetsAsString(ItemSets itemSets){
        StringBuilder builder = new StringBuilder();

        for(ItemSet itemSet : itemSets.getSets()){
          builder.append(itemSet.toString());
        }
        return builder.toString();
    }

    private List<String> getTransaction(Tuple tuple){
        String rawTransaction = (String) tuple.getValue(0);
        String[] tokens = rawTransaction.split("\\s+");
        return Arrays.asList(tokens);
    }
}